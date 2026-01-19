# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    has_discount_price = fields.Boolean(
        compute="_compute_has_discount_price",
    )
    base_price = fields.Float(compute="_compute_base_price")
    base_price_discount = fields.Float(
        digits="Discount", compute="_compute_base_price_discount"
    )

    @api.depends("base_price", "has_discount_price")
    def _compute_base_price_discount(self):
        lines_with_product = self.filtered("has_discount_price")
        for line in lines_with_product:
            line.base_price_discount = (
                ((line.base_price - line._get_pricelist_price()) / line.base_price)
                if line.base_price
                else 0.0
            )
        (self - lines_with_product).base_price_discount = 0.0

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
            if line.company_id.display_base_price_method == "discount":
                base_price = line._get_pricelist_price_before_discount()
            else:
                base_price = line._get_pricelist_price_before_pricelist()
            line.base_price = base_price
        (self - lines_with_product).base_price = False

    def _get_pricelist_price_before_pricelist(self):
        """Compute the price used as base for the pricelist price computation.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        return self.pricelist_item_id._compute_price_before_pricelist(
            product=self.product_id.with_context(**self._get_product_price_context()),
            quantity=self.product_uom_qty or 1.0,
            uom=self.product_uom,
            date=self._get_order_date(),
            currency=self.currency_id,
        )
