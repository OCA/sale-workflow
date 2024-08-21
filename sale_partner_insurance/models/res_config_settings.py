# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.Model):
    _inherit = "res.config.settings"

    coefficient_sale_insurance = fields.Float(
        related="company_id.coefficient_sale_insurance", readonly=False
    )
    insurance_product = fields.Many2one(
        related="company_id.insurance_product", readonly=False
    )
