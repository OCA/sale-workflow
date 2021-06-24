# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class SaleCouponApplyCode(models.TransientModel):
    """Extend to modify apply_coupon method for multi coupon usage."""

    _inherit = "sale.coupon.apply.code"

    def apply_coupon(self, order, coupon_code):
        # If coupon_code from program with promo code: return super
        program_model = self.env["sale.coupon.program"]
        program = program_model.search([("promo_code", "=", coupon_code)])
        if program:
            return super().apply_coupon(order, coupon_code)
        # If coupon_code from non multi-use coupon: return super
        coupon_model = self.env["sale.coupon"]
        coupon = coupon_model.search([("code", "=", coupon_code)], limit=1)
        if not coupon.multi_use:
            return super().apply_coupon(order, coupon_code)
        # If multi-use coupon, call super with passing coupon/order in context
        # to allow program compute correctly the reward line amount.
        # Not ideal,
        # but code core is not easily to override to custom this part.
        self = self.with_context(multi_use_coupon=coupon, current_order=order)
        error_status = super().apply_coupon(order, coupon_code)
        if not error_status:
            coupon.move_to_multi_use()
        return error_status
