# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_total = fields.Monetary(
        compute="_compute_amount", string="Discount Subtotal", store=True
    )
    price_subtotal_no_discount = fields.Monetary(
        compute="_compute_amount", string="Subtotal Without Discount", store=True
    )
    price_total_no_discount = fields.Monetary(
        compute="_compute_amount", string="Total Without Discount", store=True
    )

    def _update_discount_display_fields(self):
        for line in self:
            line.price_subtotal_no_discount = 0
            line.price_total_no_discount = 0
            line.discount_total = 0
            if not line.discount:
                line.price_total_no_discount = line.price_total
                line.price_subtotal_no_discount = line.price_subtotal
                continue
            price = line.price_unit
            taxes = line.tax_id.compute_all(
                price,
                line.order_id.currency_id,
                line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )

            price_subtotal_no_discount = taxes["total_excluded"]
            price_total_no_discount = taxes["total_included"]
            discount_total = price_total_no_discount - line.price_total

            line.update(
                {
                    "discount_total": discount_total,
                    "price_subtotal_no_discount": price_subtotal_no_discount,
                    "price_total_no_discount": price_total_no_discount,
                }
            )

    @api.model
    def _get_compute_amount_depends(self):
        return ["product_uom_qty", "discount", "price_unit", "tax_id"]

    @api.depends(lambda self: self._get_compute_amount_depends())
    def _compute_amount(self):
        res = super()._compute_amount()
        self._update_discount_display_fields()
        return res
