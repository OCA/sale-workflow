# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_invoice_commercial_partner_filter = fields.Boolean(
        related="company_id.use_invoice_commercial_partner_filter",
        readonly=False,
    )
    use_shipping_commercial_partner_filter = fields.Boolean(
        related="company_id.use_shipping_commercial_partner_filter",
        readonly=False,
    )
