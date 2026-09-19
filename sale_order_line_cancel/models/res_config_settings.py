# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    on_sale_line_cancel_decrease_line_qty = fields.Boolean(
        related="company_id.on_sale_line_cancel_decrease_line_qty", readonly=False
    )
