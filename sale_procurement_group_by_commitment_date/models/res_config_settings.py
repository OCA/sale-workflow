# Copyright ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sale_group_by_commitment_date = fields.Boolean(
        related="company_id.sale_group_by_commitment_date", readonly=False
    )
