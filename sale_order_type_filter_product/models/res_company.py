# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_order_type_invalid_product_action = fields.Selection(
        selection=[
            ("prevent", "Prevent Sale Order Type Change"),
            ("remove", "Remove Invalid Sale Order Lines"),
        ],
        string="Invalid Products on Sale Order Type Change",
        default="prevent",
        required=True,
        help=(
            "Defines what happens when changing the sale order type if the "
            "order contains products that are not allowed for the new type."
        ),
    )
