from odoo import fields, models


class LoyaltyReward(models.Model):
    _inherit = "loyalty.reward"

    discount_product_ids = fields.Many2many(
        "product.product", domain=[("loyalty_exclude", "=", False)]
    )
