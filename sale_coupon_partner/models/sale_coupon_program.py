# Copyright 2021 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleCouponProgram(models.Model):
    _inherit = "sale.coupon.program"

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
