# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    """Extend to implement most_expensive_product disc option."""

    _inherit = "sale.order"

    def _get_most_expensive_line(self):
        # Mimic _get_cheapest_line method.
        price_reduce_digits = self.env["decimal.precision"].precision_get(
            self.order_line._fields["price_reduce"]._digits
        )
        lines = self.order_line.filtered(
            lambda r: not r.is_reward_line
            and float_compare(r.price_reduce, 0, precision_digits=price_reduce_digits)
            > 0
        )
        return max(lines, key=lambda r: r["price_reduce"])

    def _get_cheapest_line(self):
        if self._context.get("use_most_expensive_line"):
            return self._get_most_expensive_line()
        return super()._get_cheapest_line()

    def _get_reward_values_discount(self, program):
        if (
            # Make sure we don't overwrite checks order.
            program.discount_type != "fixed_amount"
            and program.discount_apply_on == "most_expensive_product"
        ):
            # Original _get_reward_values_discount implementation is
            # crappy. It makes cumbersome to extend it. To avoid having
            # to copy/paste and overwrite this method, we instead make
            # it work as if cheapest_product option is used. In this
            # case, all we need is to intercept _get_cheapest_line with
            # context.
            program = self.env["sale.coupon.program"].new(
                values={"discount_apply_on": "cheapest_product"}, origin=program
            )
            self = self.with_context(use_most_expensive_line=True)
        return super(SaleOrder, self)._get_reward_values_discount(program)
