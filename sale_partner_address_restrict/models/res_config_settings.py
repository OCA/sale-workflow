# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_partner_address_restriction = fields.Boolean(
        related="company_id.sale_partner_address_restriction",
        readonly=False,
    )
