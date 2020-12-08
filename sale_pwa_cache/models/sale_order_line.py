# Copyright 2020 Tecnactiva - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    uom_factor = fields.Float(related="product_uom.factor", store=False, readonly=True)
    uom_rounding = fields.Float(related="product_uom.rounding", store=False, readonly=True)
    uom_category_id = fields.Many2one(related="product_id.uom_id.category_id", store=False, readonly=True)
