# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_commitment_date_required = fields.Boolean(
        string="Delivery Date Required",
        help="Require the delivery date to confirm a sales order.",
    )
