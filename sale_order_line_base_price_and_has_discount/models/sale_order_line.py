# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    has_discount_price = fields.Boolean(
        compute="_compute_has_discount_price",
    )
    base_price = fields.Float(compute="_compute_base_price")

    @api.depends("product_id", "order_id.pricelist_id", "base_price")
    def _compute_has_discount_price(self):
        lines_with_product = self.filtered("product_id")
        for line in lines_with_product:
            pricelist_price = line._get_pricelist_price()
            base_price = line.base_price
            line.has_discount_price = bool(pricelist_price < base_price)
        (self - lines_with_product).has_discount_price = False

    @api.depends("product_id")
    def _compute_base_price(self):
        lines_with_product = self.filtered("product_id")
        for line in lines_with_product:
            base_price = line._get_pricelist_price_before_discount()
            line.base_price = base_price
        (self - lines_with_product).base_price = False
