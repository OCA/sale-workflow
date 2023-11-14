# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    force_zero_units_included = fields.Boolean()
    sale_line_recommendation_domain = fields.Char(default="[]")
