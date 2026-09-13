# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    display_base_price_method = fields.Selection(
        selection=[
            ("discount", "Discounts only"),
            ("discount_formula", "Discount and Formula"),
        ],
        default="discount",
        required=True,
        help="Choose the method to display the base price "
        "(to include or not formula based pricelists)",
    )
