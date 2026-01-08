# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_auto_validation = fields.Boolean(
        string="POs Auto Validation",
        help="When a purchase order is created from a sales order "
        "using the MTO or Dropship rule for this company, "
        "it will be automatically validated.",
    )
