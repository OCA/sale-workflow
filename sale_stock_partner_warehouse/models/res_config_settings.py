# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_warehouse_by_partner_shipping = fields.Boolean(
        related="company_id.sale_warehouse_by_partner_shipping",
        readonly=False,
    )
