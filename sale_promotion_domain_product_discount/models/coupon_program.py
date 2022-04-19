from odoo import api, models


class CouponProgram(models.Model):
    _inherit = "coupon.program"

    @api.onchange("reward_type")
    def _onchange_reward_type(self):
        """
        Set discount type as discount if reward type is discount_line
        """
        if self.reward_type == "discount_line":
            self.discount_type = "percentage"
