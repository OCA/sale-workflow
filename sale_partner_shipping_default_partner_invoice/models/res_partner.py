# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_partner_invoice_id = fields.Many2one(
        "res.partner",
        string="Default Invoice Address",
        help="The specified partner will be proposed as the invoice address in "
        "the sales order when this address is set as the shipping address.",
    )
