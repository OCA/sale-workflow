# Copyright 2021 Manuel Calero Solís (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    unit_weight = fields.Float(
        string='Unit Weight',
        digits=dp.get_precision('Stock Weight'),
    )
    total_ordered_weight = fields.Float(
        compute='_compute_total_ordered_weight',
        string='Total Ordered Weight',
        store=True
    )
    total_delivered_weight = fields.Float(
        compute='_compute_total_delivered_weight',
        string='Total Delivered Weight',
        store=True
    )

    @api.onchange('product_id')
    def _onchange_weight(self):
        for line in self:
            line.unit_weight = line.product_id.weight

    @api.depends('unit_weight', 'product_uom_qty')
    def _compute_total_ordered_weight(self):
        for line in self:
            line.total_ordered_weight = line.unit_weight * line.product_uom_qty

    @api.depends('unit_weight', 'qty_delivered')
    def _compute_total_delivered_weight(self):
        for line in self:
            line.total_delivered_weight = line.unit_weight * line.qty_delivered
