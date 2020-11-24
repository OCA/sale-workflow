# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleCouponApplyCode(models.TransientModel):
    """Extend to modify apply_coupon method for multi coupon usage."""

    _inherit = "sale.coupon.apply.code"

    def apply_coupon(self, order, coupon_code):
        """Extend to pass order coupon ctx for multi coupon usage."""
        self = self.with_context(coupon_sale_order=order, coupon_code=coupon_code)
        return super(SaleCouponApplyCode, self).apply_coupon(order, coupon_code)
