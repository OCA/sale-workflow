# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    from_default_level_packaging_id = fields.Many2one(
        comodel_name="product.packaging",
        related="product_id.from_default_level_packaging_id",
    )
