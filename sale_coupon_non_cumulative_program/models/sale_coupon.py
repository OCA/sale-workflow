# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleCouponProgram(models.Model):
    _inherit = "sale.coupon.program"

    is_cumulative = fields.Boolean(string="None-cumulative Promotion")
