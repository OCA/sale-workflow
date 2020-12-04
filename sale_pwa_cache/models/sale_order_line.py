# Copyright 2020 Tecnactiva - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    secondary_uom_factor = fields.Float(related="secondary_uom_id.factor", store=False, readonly=True)
    secondary_uom_rounding = fields.Float(related="secondary_uom_id.uom_id.rounding", store=False, readonly=True)
    uom_factor = fields.Float(related="product_uom.factor", store=False, readonly=True)
    uom_rounding = fields.Float(related="product_uom.rounding", store=False, readonly=True)
    uom_category_id = fields.Many2one(related="product_id.uom_id.category_id", store=False, readonly=True)

    @api.onchange('secondary_uom_id')
    def _onchange_secondary_uom_id(self):
        self.secondary_uom_factor = self.secondary_uom_id.factor
        self.secondary_uom_rounding = self.secondary_uom_id.uom_id.rounding
