# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_sale_multiple_vals(self, product_or_template):
        # Get product variant if we got a single variant template
        product = product_or_template
        if product._name == "product.template":
            product = product.product_variant_id

        if multiple_uom := product.sale_multiple_uom_id:
            return {
                "is_multiple": 1,
                "sale_multiple_qty": multiple_uom.factor,
            }
        return {
            "is_multiple": 0,
            "sale_multiple_qty": 1,
        }

    @api.model
    def _get_additionnal_combination_info(
        self, product_or_template, quantity, uom, date, website
    ):
        # OVERRIDE: to update the combination info with the multiple related info
        combination_info = super()._get_additionnal_combination_info(
            product_or_template, quantity, uom, date, website
        )
        combination_info.update(self._get_sale_multiple_vals(product_or_template))
        return combination_info
