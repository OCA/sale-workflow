# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_compare


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.depends(
        "order_line.discount_total",
        "order_line.discount_total",
        "order_line.is_promotion_line",
    )
    def _compute_discount(self):
        super(SaleOrder, self)._compute_discount()
        for order in self:
            discount_total = order.discount_total
            price_total_no_discount = order.price_total_no_discount
            for line in order.order_line:
                if not line.is_promotion_line:
                    continue
                price_total = line.price_total
                if (
                    float_compare(
                        line.price_total,
                        0.0,
                        precision_rounding=line.currency_id.rounding,
                    )
                    < 1
                ):
                    price_total = -price_total
                discount_total += price_total
                price_total_no_discount += price_total

            if (
                float_compare(
                    discount_total,
                    order.discount_total,
                    precision_rounding=order.currency_id.rounding,
                )
                != 0
            ):
                order.update(
                    {
                        "discount_total": discount_total,
                        "price_total_no_discount": price_total_no_discount,
                    }
                )
