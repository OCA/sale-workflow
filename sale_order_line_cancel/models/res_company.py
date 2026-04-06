# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    on_sale_line_cancel_decrease_line_qty = fields.Boolean(
        "On sale order line cancel decrease line quantity",
        help="On canceling the remaining qty to deliver of an order line "
        "it decreases the initial quantity",
    )
