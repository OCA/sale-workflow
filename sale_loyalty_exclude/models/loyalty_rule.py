from odoo import fields, models


class LoyaltyRule(models.Model):
    _inherit = "loyalty.rule"

    product_ids = fields.Many2many(domain=[("loyalty_exclude", "=", False)])
