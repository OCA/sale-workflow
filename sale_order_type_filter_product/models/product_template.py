# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_order_type_ids = fields.Many2many(
        comodel_name="sale.order.type",
        string="Sale Order Types",
        help="Sale order types for which this product is allowed.",
    )
