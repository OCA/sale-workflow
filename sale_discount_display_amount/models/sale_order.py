# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    discount_total = fields.Monetary(
        compute="_compute_discount_total",
        string="Discount Subtotal",
        currency_field="currency_id",
        store=True,
    )
    price_total_no_discount = fields.Monetary(
        compute="_compute_discount_total",
        string="Subtotal Without Discount",
        currency_field="currency_id",
        store=True,
    )

    @api.depends("order_line.discount_total", "order_line.price_total_no_discount")
    def _compute_discount_total(self):
        for order in self:
            discount_total = sum(order.order_line.mapped("discount_total"))
            price_total_no_discount = sum(
                order.order_line.mapped("price_total_no_discount")
            )
            order.update(
                {
                    "discount_total": discount_total,
                    "price_total_no_discount": price_total_no_discount,
                }
            )
