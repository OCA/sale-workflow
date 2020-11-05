from odoo import models


class SaleCouponApplyCode(models.TransientModel):
    """Extend to modify apply_coupon method for multi coupon usage."""

    _inherit = "sale.coupon.apply.code"

    def apply_coupon(self, order, coupon_code):
        """Extend to pass order coupon ctx for multi coupon usage."""
        self = self.with_context(
            coupon_order_data={
                "order": order,
                # To save original amount, before any discounts are
                # applied.
                "amount_total": order.amount_total,
            }
        )
        return super(SaleCouponApplyCode, self).apply_coupon(order, coupon_code)
