# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

REF_POLICY_SELECTION = [
    ("sync", "Always"),
    ("never", "Never"),
]


class ResCompany(models.Model):
    _inherit = "res.company"

    show_client_order_ref_sale = fields.Boolean()
    show_client_order_ref_invoice = fields.Boolean()
    client_order_ref_in_invoice_line_desc = fields.Boolean()
    so_line_client_ref_policy = fields.Selection(
        selection=REF_POLICY_SELECTION,
        string="SO Line Customer Order Ref Sync Policy",
        default="sync",
        required=True,
    )
