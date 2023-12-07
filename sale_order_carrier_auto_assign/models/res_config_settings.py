# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    carrier_auto_assign = fields.Boolean(
        related="company_id.carrier_auto_assign",
        readonly=False,
        help="Enable carrier auto assign on sale order confirmation.",
    )
