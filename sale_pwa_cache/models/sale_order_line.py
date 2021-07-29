# Copyright 2020 Tecnactiva - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    uom_factor = fields.Float(related="product_uom.factor", store=False, readonly=True)
    uom_rounding = fields.Float(
        related="product_uom.rounding", store=False, readonly=True
    )
