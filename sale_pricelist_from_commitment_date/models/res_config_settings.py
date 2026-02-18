# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_require_commitment_date = fields.Boolean(
        related="company_id.sale_require_commitment_date",
        readonly=False,
    )
    sale_commitment_date_in_header = fields.Boolean(
        related="company_id.sale_commitment_date_in_header",
        readonly=False,
    )
