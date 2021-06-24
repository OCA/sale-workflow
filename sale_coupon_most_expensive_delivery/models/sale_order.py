# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import float_compare


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_most_expensive_line(self):
        # Copied from sale_coupon_most_expensive module to ignore deliveries
        price_reduce_digits = self.env["decimal.precision"].precision_get(
            self.order_line._fields["price_reduce"]._digits
        )
        lines = self.order_line.filtered(
            lambda r: not (r.is_reward_line or r.is_delivery)
            and float_compare(r.price_reduce, 0, precision_digits=price_reduce_digits)
            > 0
        )
        return max(lines, key=lambda r: r["price_reduce"])
