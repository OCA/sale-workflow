# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    restrict_so_invoicing = fields.Boolean(
        string="Restrict invoicing from sales orders",
        help="If enabled, only members of the 'Invoice Sales Orders' group can "
        "create invoices from this company's sales orders.",
    )
