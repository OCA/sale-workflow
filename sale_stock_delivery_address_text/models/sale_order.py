# Copyright 2026 Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    delivery_address_text = fields.Text(
        string="Delivery Address (Free Text)",
        help="Free-text delivery address, meant for generic customers "
        "(e.g. walk-in customers) when you do not want to create a child "
        "contact for every sale. It is shown on the related transfers and "
        "printed on the delivery reports.",
    )
