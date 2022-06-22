# Copyright (c) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_discount_limit = fields.Float(string="Discount Limit", default=20)
