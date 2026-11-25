# Copyright 2026 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    restrict_partner_id = fields.Many2one(
        "res.partner", "Stock Owner", help="Restrict using stock from specified partner"
    )
