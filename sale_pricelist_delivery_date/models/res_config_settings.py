# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_delivery_date_price = fields.Boolean(
        related="company_id.use_delivery_date_price",
        readonly=False,
    )
    is_delivery_date_required = fields.Boolean(
        related="company_id.is_delivery_date_required",
        readonly=False,
    )
