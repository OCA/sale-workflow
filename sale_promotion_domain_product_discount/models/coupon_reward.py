from odoo import fields, models


class CouponReward(models.Model):
    _inherit = "coupon.reward"

    discount_apply_on = fields.Selection(
        selection_add=[("domain_product", "On Domain Matching Products")],
    )
    reward_type = fields.Selection(
        selection_add=[("discount_line", "Discount in Line")],
    )
