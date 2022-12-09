# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from datetime import datetime

from psycopg2 import sql
from psycopg2.extras import execute_values

from odoo import fields, models, tools


class PricelistCache(models.Model):
    """This model aims to store all product prices for all pricelists.

    Main entrypoint:
    PricelistCache::cron_reset_pricelist_cache()
    This method flushes yesterday's cache and creates a new one.

    Secondary entrypoints:
      - Product is created
        -> product_product.py::create,write
      - Pricelist is created;
        -> entrypoint product_pricelist.py::create

    The idea is that, the price you get is the price of today.
    If you modify a price, the price will be updated tomorrow.
    This avoids created a lot of logic to maintain this cache up to date, which
    would be very complex and not that reliable.

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

    # def _create_cache_records__get_sql_values(self, pricelist_id, product_prices):
    # """Returns a set of row values for sql INSERT."""
    # dataset = self._cache_product_prices__get_create_values(
    # pricelist_id, product_prices
    # )
    # # TODO Should use sql.SQL
    # sql_set = [", ".join(map(str, data)) for data in dataset]
    # return "), (".join(sql_set)

    def _create_cache_records__get_create_columns(self):
        return ["product_id", "pricelist_id", "price"]

    def _create_cache_records__get_insert_clause(self):
        """Returns the INSERT clause template for the INSERT query."""
        template = "INSERT INTO product_pricelist_cache ({columns})"
        columns = self._create_cache_records__get_create_columns()
        sql_columns = ", ".join(columns)
        return template.format(columns=sql_columns)

    def _create_cache_records__get_values_clause(self):
        """Returns the VALUES clause template for the INSERT SQL query."""
        return "VALUES %s"

    def _create_cache_records__get_sql_template_parts(self):
        """Returns all clause templates for the INSERT sql query."""
        return [
            self._create_cache_records__get_insert_clause(),
            self._create_cache_records__get_values_clause(),
        ]

    def _create_cache_records__get_sql_template(self):
        """Returns the SQL formatted INSERT query template."""
        return "\n".join(self._create_cache_records__get_sql_template_parts())

    def _create_cache_records__get_row_values(self, product_id, pricelist_id, price):
        """Returns a set of values corresponding to a row in the INSERT sql query."""
        # for a set of values (product_id, (price, )), create the row values
        # (product_id, pricelist_id, )
        return (product_id, pricelist_id, price)

    def _create_cache_records__get_raw_values(self, pricelist_id, product_prices):
        """Returns a set of rows, to be formatted for the INSERT SQL query."""
        res = set()
        for product_id, price in product_prices.items():
            values = self._create_cache_records__get_row_values(
                product_id, pricelist_id, price
            )
            res.add(values)
        return list(res)

    def _cache_product_prices__create_cache_records(self, pricelist_id, product_prices):
        """Create price cache records for a given pricelist, applied to a list of
        product ids.

        args:
            - pricelist_id : The pricelist id on which prices are applied
            - product_ids : A list of product ids to cache
            - product_prices : A dict containing the prices for each product
        """
        raw_values = self._create_cache_records__get_raw_values(
            pricelist_id, product_prices
        )
        if raw_values:
            sql_template = self._create_cache_records__get_sql_template()
            self.flush()
            execute_values(self.env.cr, sql_template, raw_values)

    def create_product_pricelist_cache(self, product_ids=None, pricelist_ids=None):
        """Creates cache records given a recordset of products and pricelists.

        If product_ids is None, all products will be cached.
        If pricelist_ids is None, it will create the cache for all pricelists.
        """
        # Here, the table has been flushed before running this.
        # we assume we only have to create records.
        # TODO: see README.rst
        # If in the future we have to update the cache (which is not what we want)
        # We will have to adapt this method
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
            self._cache_product_prices__create_cache_records(
                pricelist.id, product_prices
            )
            # Once this is done, set pricelist cache as computed on pricelist
            pricelist.is_pricelist_cache_computed = True

    def create_full_cache(self):
        """Creates cache for all prices applied to all pricelists."""
        pricelists = self.env["product.pricelist"].search([])
        pricelist_ids = pricelists.ids
        # Spawn a job every 3 pricelists (reduce the number of jobs created)
        for chunk_ids in tools.misc.split_every(3, pricelist_ids):
            self.with_delay().create_product_pricelist_cache(pricelist_ids=chunk_ids)

    def flush_pricelist_cache(self):
        # flush table
        flush_query = "TRUNCATE TABLE product_pricelist_cache CASCADE;"
        self.env.cr.execute(flush_query)
        # reset sequence
        sequence_query = """
            ALTER SEQUENCE product_pricelist_cache_id_seq RESTART WITH 1;
        """
        self.env.cr.execute(sequence_query)
        self.env["product.pricelist"].search([]).is_pricelist_cache_computed = False

    def cron_reset_pricelist_cache(self):
        """Recreates the whole price list cache."""
        self.flush_pricelist_cache()
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
