# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    catalog_ignore_last_price = fields.Boolean(
        string="Ignore Last Sale Price in Catalog",
        help="When the sale catalog shows the last sale prices, the products of "
        "this category keep the pricelist price.",
    )
