# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_auto_cancel = fields.Boolean(
        string="Propagate cancellation on MTO/Dropshipping",
        help="When a purchase order is created from a sales order "
        "using the MTO or Dropship rule for this company, "
        "and the sale order is cancelled, it will be automatically cancelled.",
    )
