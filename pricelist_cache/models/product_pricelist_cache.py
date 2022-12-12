# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

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

    @classmethod
    def _format_sql_values(cls, values):
        sql_values = []
        for vals in values:
            sql_vals = map(sql.Literal, vals)
            sql_values.append(sql_vals.join(", "))
        return sql_values

    def _create_cache_records(self, pricelist_id, product_prices):
        """Create price cache records for a given pricelist, applied to a list of
        product ids.

        args:
            - pricelist_id : The pricelist id on which prices are applied
            - product_prices : A dict containing the prices for each product
        """
        values = [
            sql.SQL(", ").join(
                map(sql.Literal, (product_id, pricelist_id, product_price))
            )
            for product_id, product_price in product_prices.items()
        ]
        if values:
            # create_everything from a single transaction
            query = sql.SQL(
                """
                INSERT INTO product_pricelist_cache (product_id, pricelist_id, price)
                VALUES ({});
            """
            ).format(sql.SQL("), (").join(values))
            self.flush()
            self.env.cr.execute(query)

    def create_product_pricelist_cache(self, product_ids=None, pricelist_ids=None):
        """
        Updates price list cache given a product.product recordset and a pricelist,
        if specified.
        """
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
        for pricelist in pricelists:
            product_ids_to_cache = pricelist._get_product_ids_to_cache(product_ids)
            product_prices = pricelist._get_product_prices(product_ids_to_cache)
            self._create_cache_records(pricelist.id, product_prices)

    def create_full_cache(self):
        """Creates cache for all prices applied to all pricelists."""
        pricelist_ids = self.env["product.pricelist"].search([]).ids
        # Spawn a job every 3 pricelists (reduce the number of jobs created)
        for chunk_ids in tools.misc.split_every(3, pricelist_ids):
            self.with_delay().create_product_pricelist_cache(pricelist_ids=chunk_ids)

    def _reset_table(self):
        # flush table
        flush_query = "TRUNCATE TABLE product_pricelist_cache CASCADE;"
        self.env.cr.execute(flush_query)
        # reset sequence
        sequence_query = """
            ALTER SEQUENCE product_pricelist_cache_id_seq RESTART WITH 1;
        """
        self.env.cr.execute(sequence_query)

    def cron_reset_pricelist_cache(self):
        """Recreates the whole price list cache."""
        self._reset_table()
        # Re-create everything
        self.create_full_cache()

    def get_cached_prices_for_pricelist(self, pricelist, products):
        """Retrieves product prices for a given pricelist."""
        # Retrieve cache for the current pricelist first
        cached_prices = self.search(
            [
                ("pricelist_id", "=", pricelist.id),
                ("product_id", "in", products.ids),
            ]
        )
        # Then, retrieves prices from parent pricelists
        remaining_products = products - cached_prices.mapped("product_id")
        parent_pricelists = pricelist._get_parent_pricelists()
        # There shouldn't be multiple parents for a pricelist, but it's possible…
        for parent_pricelist in parent_pricelists:
            cached_prices |= self.get_cached_prices_for_pricelist(
                parent_pricelist, remaining_products
            )
        return cached_prices

    def _get_tree_view(self, domain=None):
        xmlid = "pricelist_cache.product_pricelist_cache_action"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if domain is not None:
            action["domain"] = domain
        return action
