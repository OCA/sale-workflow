# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sales_cutoff_calendar = fields.Many2one(
        related="company_id.sales_cutoff_calendar", readonly=False
    )
