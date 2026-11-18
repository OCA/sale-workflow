# Copyright 2026 Aures Tic Consultors S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductCustomerinfo(models.Model):
    _inherit = "product.customerinfo"

    sale_qty_multiple = fields.Float(
        string="Sale Multiple",
        digits="Product Unit of Measure",
        help="Quantities sold to this customer must be a multiple of this one, "
        "in the unit of measure of the product. Leave it at 0 for no restriction.",
    )
    sale_qty_multiple_policy = fields.Selection(
        [
            ("down", "Round down"),
            ("up", "Round up"),
            ("nearest", "Round to the nearest"),
            ("warning", "Only warn"),
        ],
        string="When Not a Multiple",
        default="warning",
        required=True,
        help="What to do with a sale order line whose quantity is not a multiple: "
        "round it down (e.g. 63 with a multiple of 50 becomes 50), round it up "
        "(it becomes 100), round it to the nearest multiple (halves go up: 74 "
        "becomes 50 and 75 becomes 100; never below one multiple: 20 becomes 50) "
        "or keep it and warn the user.",
    )
