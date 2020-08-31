# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleCouponApplyCode(models.TransientModel):
    _inherit = "sale.coupon.apply.code"

    def apply_coupon(self, order, coupon_code):
        # creating reward lines and recording programs correctly handled in
        # initial method, here we providing recomputation to pricelist
        error_status = super().apply_coupon(order, coupon_code)
        if error_status:
            return error_status
        program = self.env["sale.coupon.program"].search(
            [("promo_code", "=", coupon_code)]
        )
        if program:
            if (
                program.promo_applicability == "on_current_order"
                and program.reward_type == "use_pricelist"
            ):
                order._update_pricelist(program.reward_pricelist_id)
        else:
            coupon = self.env["sale.coupon"].search(
                [("code", "=", coupon_code)], limit=1
            )
            if coupon and coupon.reward_pricelist_id:
                order._update_pricelist(coupon.reward_pricelist_id)
        return error_status
