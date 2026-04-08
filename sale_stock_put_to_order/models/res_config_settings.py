# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pto_auto_select_location = fields.Boolean(
        string="Auto-select PTO destination",
        config_parameter="sale_stock_put_to_order.auto_select_location",
        help=(
            "Automatically assign the put-to-order proposed bin as the "
            "destination on move lines during reservation."
        ),
    )
