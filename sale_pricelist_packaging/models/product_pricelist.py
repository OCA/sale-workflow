# Copyright 2025 Akretion (https://www.akretion.com).
# @author Mathieu DELVA <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    packaging_id = fields.Many2one("product.packaging")

    def _is_applicable_for(self, product, qty_in_product_uom):
        ctx = self.env.context
        print("### _is_applicable_for TRIGGERED", ctx)
        if "packaging" in ctx:
            if ctx["packaging"] == self.packaging_id:
                return super()._is_applicable_for(product, qty_in_product_uom)
            return False

        elif "packaging" not in ctx and self.packaging_id:
            return False

        return super()._is_applicable_for(product, qty_in_product_uom)
