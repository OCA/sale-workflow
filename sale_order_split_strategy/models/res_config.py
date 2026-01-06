# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_order_split_strategy_errors = fields.Selection(
        related="company_id.sale_order_split_strategy_errors",
        readonly=False,
    )
