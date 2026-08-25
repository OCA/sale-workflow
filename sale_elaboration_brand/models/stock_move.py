# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    product_brand_id = fields.Many2one(
        "product.brand", string="Brand", related="product_id.product_brand_id"
    )
