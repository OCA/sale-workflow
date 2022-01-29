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

    def _update_existing_records(self, product_prices):
        """Update existing records with provided prices.

        Args:
            - self : The recordset of cache records to update
            - product_prices : The new prices to apply
        """
        # Write everything in single transaction
        values = [
            sql.SQL(", ").join(
                map(sql.Literal, (record.id, product_prices[record.product_id.id]))
            )
            for record in self
        ]
        query = sql.SQL(
            """
            UPDATE
                product_pricelist_cache AS pricelist_cache
            SET
                price = c.price
            FROM (VALUES ({}))
                AS c(id, price)
            WHERE
                c.id = pricelist_cache.id;
        """
        ).format(sql.SQL("), (").join(values))
        self.flush()
        self.env.cr.execute(query)
        self.invalidate_cache(["price"])
        self.recompute()

    def _create_cache_records(self, pricelist_id, product_ids, product_prices):
        """Create price cache records for a given pricelist, applied to a list of
        product ids.

        args:
            - pricelist_id : The pricelist id on which prices are applied
            - product_ids : A list of product ids to cache
            - product_prices : A dict containing the prices for each product
        """
        values = [
            sql.SQL(", ").join(
                map(sql.Literal, (p_id, pricelist_id, product_prices[p_id]))
            )
            for p_id in product_ids
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

    def _update_pricelist_cache(self, pricelist_id, product_prices):
        """Updates the cache, for a given pricelist, and product prices.

        Args:
            - pricelist: a product.pricelist record
            - product_prices: A dictionnary,
              with product.product id as keys, and prices as values
        """
        product_ids = list(product_prices.keys())
        # First, update existing records
        existing_records = self.search(
            [
                ("pricelist_id", "=", pricelist_id),
                ("product_id", "in", product_ids),
            ]
        )
        if existing_records:
            existing_records._update_existing_records(product_prices)
        # Then, create missing records with provided prices
        # Diff between products and already created records
        not_cached_product_ids = set(product_ids)
        if existing_records:
            not_cached_product_ids -= set(existing_records.mapped("product_id").ids)
        if not_cached_product_ids:
            self._create_cache_records(
                pricelist_id, not_cached_product_ids, product_prices
            )

    def _get_product_ids_to_update(self, pricelist, product_ids):
        """Returns a list of product_ids that are already cached
        for the given pricelist.

        Args:
            - pricelist: The pricelist record on which new prices are applied
            - product_prices: The list of products to check
        """
        product_ids_to_update = []
        # We need to be sure to not waste resources while updating the cache.
        # To do that, we ensure that prices are not coming from a parent
        # pricelist.
        if pricelist._get_parent_pricelists():
            # If this is a factor pricelist, then everything
            # have to be updated
            if pricelist._is_factor_pricelist():
                product_ids_to_update = product_ids
            # Otherwise, prices are fetched from parent pricelist
            # and only products in items have to be updated
            else:
                product_item_ids = pricelist.item_ids.filtered(
                    lambda i: i.product_id.id in product_ids
                )
                product_ids_to_update = product_item_ids.mapped("product_id").ids
        else:
            # No parent (for instance public pricelist), then update everything
            product_ids_to_update = product_ids
        return product_ids_to_update

    def update_product_pricelist_cache(self, product_ids=None, pricelist_ids=None):
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
            product_ids_to_update = self._get_product_ids_to_update(
                pricelist, product_ids
            )
            product_prices = pricelist._get_product_prices(product_ids_to_update)
            self._update_pricelist_cache(pricelist.id, product_prices)

    def _update_pricelist_items_cache(self, pricelist_items):
        """Updates cache for a given recordset of pricelist items, then update
        the items skipped state to False.
        """
        pricelist_products = pricelist_items._get_pricelist_products_group()
        for pricelist_id, product_ids in pricelist_products.items():
            self.with_delay().update_product_pricelist_cache(
                product_ids=product_ids, pricelist_ids=[pricelist_id]
            )
        pricelist_items.write({"pricelist_cache_update_skipped": False})

    def create_full_cache(self):
        """Creates cache for all prices applied to all pricelists."""
        pricelist_ids = self.env["product.pricelist"].search([]).ids
        # Spawn a job every 3 pricelists (reduce the number of jobs created)
        for chunk_ids in tools.misc.split_every(3, pricelist_ids):
            self.with_delay().update_product_pricelist_cache(pricelist_ids=chunk_ids)

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

    def get_cached_prices_for_pricelist(self, pricelist, products):
        """Retrieves product prices for a given pricelist."""
        # As some items might have been skipped during product_pricelist_item
        # updates, some cached prices might be wrong, since those records
        # will be updated during a daily cron task.
        # If any of those prices is queried here, update cache before retrieving it
        need_update_items = self.env["product.pricelist.item"].search(
            [
                ("pricelist_id", "=", pricelist.id),
                ("product_id", "in", products.ids),
                ("pricelist_cache_update_skipped", "=", True),
            ]
        )
        self._update_pricelist_items_cache(need_update_items)
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
