from odoo import models


class SaleOrder(models.Model):
    """Extend to modify action_confirm for multi-use coupons."""

    _inherit = "sale.order"

    # TODO: implement multi-use coupon relation on sale.order ->
    # applied_coupon_ids is o2m, which removes coupon if same coupon
    # is applied on another SO. But for multi-use coupon, it must be
    # able to keep same coupon on multiple sale orders.
    # TODO: action_draft seems buggy, because it does not reset back
    # coupons to new state (you can abuse coupon this way and use normal
    # coupon multiple times).

    def action_confirm(self):
        """Extend to pass coupon_sale_order context."""
        for order in self:
            order = order.with_context(coupon_sale_order=order)
            super(SaleOrder, order).action_confirm()
        return True

    def action_cancel(self):
        """Extend to pass coupon_sale_order context."""
        # NOTE. Can't rely on coupon/SO relation, because
        # applied_coupon_ids is o2m field, meaning same coupon used on
        # another SO, would make lose relation on previous SO.
        for order in self:
            order = order.with_context(coupon_sale_order=order)
            super(SaleOrder, order).action_cancel()
        return True
