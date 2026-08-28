# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    @api.model
    def _get_compute_price_methods_for_base_price_pricelist(self):
        return ["percentage", "formula"]

    def _compute_price_before_pricelist(self, *args, **kwargs):
        """Compute the base price of the lowest pricelist rule,
        taking into account percentage and formula items
        """
        pricelist_item = self
        methods = self._get_compute_price_methods_for_base_price_pricelist()
        while pricelist_item.base == "pricelist":
            rule_id = pricelist_item.base_pricelist_id._get_product_rule(
                *args, **kwargs
            )
            rule_pricelist_item = self.env["product.pricelist.item"].browse(rule_id)
            if rule_pricelist_item and rule_pricelist_item.compute_price in methods:
                pricelist_item = rule_pricelist_item
            else:
                break

        return pricelist_item._compute_base_price(*args, **kwargs)
