# Copyright (C) 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_need_po = fields.Boolean(
        string="Customer Requires PO",
        tracking=True,
        help="A PO number will be required on the"
        " Sales Order field for Customer Reference",
    )
    sale_doc = fields.Text(
        string="Sales Require Documentation",
        tracking=True,
        help="Details of the sales documentation required for this customer."
        " Sales documentation notes field will be required on Sales Orders"
        " This is complementary to requiring a PO number, and can be used"
        " with or without that setting.",
    )
