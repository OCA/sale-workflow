# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('order_id.state', 'procurement_ids.state', 'product_uom_qty')
    def _compute_qty_to_deliver(self):
        for line in self:
            total = 0.0
            for move in line.procurement_ids.mapped('move_ids').filtered(
                    lambda m: m.state not in ('cancel', 'done')):
                if move.product_uom != line.product_uom:
                    total += move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom)
                else:
                    total += move.product_uom_qty
            line.qty_to_deliver = total

    qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver',
                                  digits=dp.get_precision(
                                      'Product Unit of Measure'),
                                  copy=False,
                                  string="Qty to Deliver", store=True)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_qty_to_invoice(self):
        for so in self:
            so.qty_to_invoice = sum(so.mapped('order_line.qty_to_invoice'))

    def _compute_qty_to_deliver(self):
        for so in self:
            so.qty_to_deliver = sum(so.mapped('order_line.qty_to_deliver'))

    @api.model
    def _search_qty_to_invoice(self, operator, value):
        so_line_obj = self.env['sale.order.line']
        res = []
        so_lines = so_line_obj.search(
            [('qty_to_invoice', operator, value)])
        order_ids = so_lines.mapped('order_id')
        res.append(('id', 'in', order_ids.ids))
        return res

    @api.model
    def _search_qty_to_deliver(self, operator, value):
        so_line_obj = self.env['sale.order.line']
        res = []
        so_lines = so_line_obj.search(
            [('qty_to_deliver', operator, value)])
        order_ids = so_lines.mapped('order_id')
        res.append(('id', 'in', order_ids.ids))
        return res

    qty_to_invoice = fields.Float(compute='_compute_qty_to_invoice',
                                  search='_search_qty_to_invoice',
                                  string="Qty to Bill",
                                  default=0.0)
    qty_to_deliver = fields.Float(compute='_compute_qty_to_deliver',
                                  search='_search_qty_to_deliver',
                                  string="Qty to Deliver",
                                  default=0.0)
