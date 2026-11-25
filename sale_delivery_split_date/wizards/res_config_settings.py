# Copyright 2026 Binhex
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_delivery_split_date = fields.Boolean(
        related="company_id.sale_delivery_split_date", readonly=False
    )
