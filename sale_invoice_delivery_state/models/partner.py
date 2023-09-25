# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_policy = fields.Selection(
        [("partially", "Partially Delivered"), ("fully", "Fully Delivered")],
        help="Partially Delivered: Invoice when the customer is partially delivered.\n"
        "Fully Delivered: Invoice when the customer is fully delivered.",
        default="partially",
    )
