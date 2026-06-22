# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    fixed_price_no_discount = fields.Boolean(
        string="Prevent Discounts on Fixed Price",
        default=True,
        help=(
            "Prevent manual discounts on sale order lines when this fixed-price "
            "rule is applied."
        ),
    )
