# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_field_on_sol = fields.Selection(
        selection=[
            ("qty_available", "On Hand"),
            ("free_qty", "Free To Use"),
            ("virtual_available", "Forecast"),
        ],
        string="Stock field on Sale Order Line",
        default="qty_available",
        config_parameter="sale_order_line_stock_info.stock_field_on_sol",
    )
