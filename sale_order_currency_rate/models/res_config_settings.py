# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_show_currency_rate = fields.Selection(
        related="company_id.sale_show_currency_rate",
        readonly=False,
    )
