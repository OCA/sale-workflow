# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    use_partner_pricelist = fields.Boolean(
        related="company_id.use_partner_pricelist",
        readonly=False,
    )
