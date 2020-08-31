# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleCouponProgram(models.Model):
    _inherit = "sale.coupon.program"

    is_cumulative = fields.Boolean(string="None-cumulative Promotion")
    reward_pricelist_id = fields.Many2one("product.pricelist", string="Pricelist")


class SaleCouponReward(models.Model):
    _inherit = "sale.coupon.reward"

    reward_type = fields.Selection(selection_add=[("use_pricelist", "Pricelist")])


class SaleCoupon(models.Model):
    _inherit = "sale.coupon"

    reward_pricelist_id = fields.Many2one(
        related="program_id.reward_pricelist_id", string="Pricelist"
    )
