# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from psycopg2 import sql

from odoo import fields, models, tools


class PricelistCache(models.Model):
    """This model aims to store all product prices depending on all pricelist.

    Price cache is updated or created in the following cases:
        - Product price is created / modified;
          -> entrypoint "product_product.py::{create,write}"
        - Pricelist item is created / modified;
          -> entrypoint "product_pricelist_item.py::update_product_pricelist_cache"
        - Pricelist is created;
          -> entrypoint "product_pricelist.py::create"
    There's also a daily cron task that updates cache prices
    that have been skipped during the day:
     - see "cron_reset_pricelist_cache" for the cron method
     - see "product_pricelist_item.py::update_product_pricelist_cache"
       for skip conditions
    Every call to PricelistCache.update_product_pricelist_cache
    should be made in a job as computation might be slow, depending on the case.
    """

    _name = "product.pricelist.cache"
    _description = "Pricelist Cache"
    _rec_name = "pricelist_id"

    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        required=True,
        index=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product", string="Product Variant", index=True
    )
    price = fields.Float()

    def _format_sql_values(self, dataset):
        sql_set = [sql.SQL(", ").join(map(sql.Literal, data)) for data in dataset]
        return sql.SQL("), (").join(sql_set)

    def _get_create_columns(self):
        return ["product_id", "pricelist_id", "price"]

    def _get_sql_create_insert_clause(self):
        columns = self._get_create_columns()
        return f"INSERT INTO product_pricelist_cache ({', '.join(columns)})"

    def _get_sql_create_values_clause(self):
        return "VALUES ({})"

    def _get_sql_create_query_template(self):
        query_string = " ".join(
            [
                self._get_sql_create_insert_clause(),
                self._get_sql_create_values_clause(),
            ]
        )
        return sql.SQL(query_string)

    def _get_row_values(self, product_id, pricelist_id, price):
        values = [product_id, pricelist_id]
        for item in price:
            values.append(item)
        return tuple(values)

    def _get_create_values(self, pricelist_id, product_prices):
        res = set()
        for product_id, prices in product_prices.items():
            for price in prices:
                res.add(self._get_row_values(product_id, pricelist_id, price))
        return res

    def _create_cache_records(self, values):
        """Create price cache records for a given pricelist, applied to a list of
        product ids.

        args:
            - pricelist_id : The pricelist id on which prices are applied
            - product_ids : A list of product ids to cache
            - product_prices : A dict containing the prices for each product
        """
        sql_values = self._format_sql_values(values)
        # create_everything from a single transaction
        sql_template = self._get_sql_create_query_template()
        # import pdb; pdb.set_trace()
        self.flush()
        self.env.cr.execute(sql_template, sql_values)

    def _cache_product_prices(self, pricelist_id, product_prices):
        values = self._get_create_values(pricelist_id, product_prices)
        if values:
            self._create_cache_records(values)

    def create_product_pricelist_cache(self, product_ids=None, pricelist_ids=None):
        # HEre, the table has been flushed before running this.
        # we assume we only have to create records.
        if not product_ids:
            product_ids = self.env["product.product"].search([]).ids
        if not pricelist_ids:
            pricelists = self.env["product.pricelist"].search([])
        else:
            # Search instead of browse, since pricelists could have been unlinked
            # between the time where records have been created / modified
            # and the time this method is executed.
            pricelists = self.env["product.pricelist"].search(
                [("id", "in", pricelist_ids)]
            )
        at_datetime = datetime.now()
        for pricelist in pricelists:
            product_ids_to_cache = pricelist._get_product_ids_to_cache(
                product_ids, at_datetime
            )
            product_prices = pricelist._get_product_prices(
                product_ids_to_cache, at_datetime.date()
            )
            self._cache_product_prices(pricelist.id, product_prices)

    def create_full_cache(self):
        """Creates cache for all prices applied to all pricelists."""
        pricelist_ids = self.env["product.pricelist"].search([]).ids
        # Spawn a job every 3 pricelists (reduce the number of jobs created)
        for chunk_ids in tools.misc.split_every(3, pricelist_ids):
            self.with_delay().create_product_pricelist_cache(pricelist_ids=chunk_ids)

    def cron_reset_pricelist_cache(self):
        """Recreates the whole price list cache."""
        # flush table
        flush_query = "TRUNCATE TABLE product_pricelist_cache CASCADE;"
        self.env.cr.execute(flush_query)
        # reset sequence
        sequence_query = """
            ALTER SEQUENCE product_pricelist_cache_id_seq RESTART WITH 1;
        """
        self.env.cr.execute(sequence_query)
        # Re-create everything
        self.create_full_cache()

    def _get_cached_price_domain(self, pricelist_id, product_ids):
        return [
            ("pricelist_id", "=", pricelist_id),
            ("product_id", "in", product_ids),
        ]

    def _get_cached_price_select_clause(self):
        return """SELECT id"""

    def _get_cached_price_from_clause(self):
        return """FROM product_pricelist_cache"""

    def _get_cached_price_where_conditions(self):
        return [
            "product_id in %(product_ids)s",
            "pricelist_id = %(pricelist_id)s",
        ]

    def _get_cached_price_where_clause(self):
        where_conditions = self._get_cached_price_where_conditions()
        return f"""WHERE {' AND '.join(where_conditions)}"""

    def _get_cached_price_query_items(self):
        return [
            self._get_cached_price_select_clause(),
            self._get_cached_price_from_clause(),
            self._get_cached_price_where_clause(),
        ]

    def _get_cached_price_query(self):
        query_items = self._get_cached_price_query_items()
        sql_items = [sql.SQL(item) for item in query_items]
        return sql.SQL(" ").join(sql_items)

    def _get_cached_price_args(self, pricelist_id, product_ids, **kwargs):
        return {"pricelist_id": pricelist_id, "product_ids": tuple(product_ids)}

    def _get_cached_prices(self, pricelist_id, product_ids, **kwargs):
        query = self._get_cached_price_query()
        args = self._get_cached_price_args(pricelist_id, product_ids, **kwargs)
        self.flush()
        # import pdb; pdb.set_trace()
        self.env.cr.execute(query, args)
        rows = self.env.cr.fetchall()
        ids = [row[0] for row in rows]
        return self.browse(ids)

    def get_cached_prices_for_pricelist(self, pricelist, products, **kwargs):
        """Retrieves product prices for a given pricelist."""
        # Retrieve cache for the current pricelist first
        cached_prices = self._get_cached_prices(pricelist.id, products.ids, **kwargs)
        # Then, retrieves prices from parent pricelists
        remaining_products = products - cached_prices.mapped("product_id")
        if remaining_products:
            parent_pricelists = pricelist._get_parent_pricelists()
            # There shouldn't be multiple parents for a pricelist, but it's possible…
            for parent_pricelist in parent_pricelists:
                cached_prices |= self.get_cached_prices_for_pricelist(
                    parent_pricelist, remaining_products, **kwargs
                )
        return cached_prices

    def _get_tree_view(self, domain=None):
        xmlid = "pricelist_cache.product_pricelist_cache_action"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if domain is not None:
            action["domain"] = domain
        return action
