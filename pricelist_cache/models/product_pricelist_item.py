# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from collections import defaultdict

from odoo import fields, models

_logger = logging.getLogger("POTATO")


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    pricelist_cache_update_skipped = fields.Boolean()

    def _has_date_range(self):
        """Returns whether any of the item records in recordset is based on dates."""
        return any(bool(record.date_start or record.date_end) for record in self)

    def _get_pricelist_products_group(self):
        """Returns a mapping of products grouped by pricelist.

        Result:
        keys: product.pricelist id
        values: product.product list of ids
        """
        pricelist_products = defaultdict(list)
        for item in self:
            pricelist_products[item.pricelist_id.id].append(item.product_id.id)
        return pricelist_products

    def already_cached(self):
        return bool(
            self.env["product.pricelist.cache"].search(
                [
                    ("pricelist_id", "=", self.pricelist_id.id),
                    ("product_id", "=", self.product_id.id),
                ]
            )
        )

    def create_product_pricelist_cache(self):
        """Executed when a product item is modified. Filters items not based
        on variants or based on dates, then updates the cache.
        """
        # Filter items not applied on variants
        items = self.filtered(lambda i: i.applied_on == "0_product_variant")
        # FIXME, when a pricelist item referencing a product is created,
        # this method is triggered multiple times, hence creating multiple cache records
        items = items.filtered(lambda i: not i.already_cached())
        # Filter items based on dates
        item_ids_to_update = []
        for item in items:
            product_item_tree = item.pricelist_id._recursive_get_items(item.product_id)
            if product_item_tree._has_date_range():
                # skip if any of the item in the tree is date based
                item.pricelist_cache_update_skipped = True
                continue
            item_ids_to_update.append(item.id)
        items_to_update = self.env["product.pricelist.item"].browse(item_ids_to_update)
        # Group per pricelist
        pricelist_products = items_to_update._get_pricelist_products_group()
        # Update cache
        cache_object = self.env["product.pricelist.cache"]
        for pricelist_id, product_ids in pricelist_products.items():
            cache_object.with_delay().create_product_pricelist_cache(
                product_ids=product_ids, pricelist_ids=[pricelist_id]
            )
