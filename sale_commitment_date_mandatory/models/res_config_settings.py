# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    commitment_date_required = fields.Boolean(
        "Commitment date mandatory",
        related="company_id.sale_commitment_date_required",
        readonly=False,
    )
