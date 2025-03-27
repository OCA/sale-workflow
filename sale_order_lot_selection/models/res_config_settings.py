# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    allow_generate_so_from_lots = fields.Boolean(
        string="Allow Generate SO from Lots",
        config_parameter="sale_order_lot_selection.allow_generate_from_lots",
        default=False,
    )
