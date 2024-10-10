# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_no_effect_on_threshold_lines(self):
        """
        Returns the lines that have no effect on the minimum amount to reach
        """
        self.ensure_one()
        lines = self.order_line.filtered(lambda line: line.product_id.loyalty_exclude)
        return lines | super()._get_no_effect_on_threshold_lines()

    def _has_all_products_loyalty_exclude(self):
        """Check if all order lines have loyalty_exclude set to True."""
        for line in self.order_line:
            if not line.product_id.loyalty_exclude:
                return False
        return True

    def _get_claimable_rewards(self, forced_coupons=None):
        if self._has_all_products_loyalty_exclude():
            return {}
        else:
            return super()._get_claimable_rewards(forced_coupons=forced_coupons)

    def _try_apply_program(self, program, coupon=None):
        if self._has_all_products_loyalty_exclude():
            return {"error": _("This code is invalid.")}
        else:
            return super()._try_apply_program(program, coupon=coupon)
