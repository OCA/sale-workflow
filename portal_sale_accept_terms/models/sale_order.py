#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    portal_accept_terms = fields.Text(
        string="Terms to accept in portal",
        help="Terms to be accepted by the user "
        "when confirming the order in the portal.",
    )
