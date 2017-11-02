# -*- coding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2015  Agile Business Group                              #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU Affero General Public License as        #
# published by the Free Software Foundation, either version 3 of the    #
# License, or (at your option) any later version.                       #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU Affero General Public Licensefor more details.                    #
#                                                                       #
# You should have received a copy of the                                #
# GNU Affero General Public License                                     #
# along with this program.  If not, see <http://www.gnu.org/licenses/>. #
#                                                                       #
#########################################################################

from openerp import fields, models, api, _
from openerp.exceptions import Warning


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot', copy=False)

    available_lot_ids = fields.Many2many(
        'stock.production.lot',
        compute="_compute_available_lot_ids")

    @api.multi
    @api.depends('product_id')
    def _compute_available_lot_ids(self):
        for rec in self.filtered(
                lambda x: x.product_id.tracking
                in ['serial', 'lot'] and x.order_id.warehouse_id):
            location = rec.order_id.warehouse_id.lot_stock_id
            quants = self.env['stock.quant'].read_group([
                ('product_id', '=', rec.product_id.id),
                ('location_id', 'child_of', location.id),
                ('qty', '>', 0),
                ('lot_id', '!=', False),
            ], ['lot_id'], 'lot_id')
            available_lot_ids = [quant['lot_id'][0] for quant in quants]
            rec.available_lot_ids = available_lot_ids

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        res = super(
            SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        res['lot_id'] = self.lot_id.id
        return res

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        """
         Idea obtained from here
         https://github.com/odoo/odoo/issues/16072#issuecomment-289833419
         by the change that was introduced in that same conversation.
        """
        for field in field_onchange.keys():
            if field.startswith('available_lot_ids.'):
                del field_onchange[field]
        return super(SaleOrderLine, self).onchange(
            values, field_name, field_onchange)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def get_move_from_line(self, line):
        move = self.env['stock.move']
        # i create this counter to check lot's univocity on move line
        lot_count = 0
        for p in line.order_id.picking_ids:
            for m in p.move_lines:
                if line.lot_id == m.restrict_lot_id:
                    move = m
                    lot_count += 1
                    # if counter is 0 or > 1 means that something goes wrong
                    if lot_count != 1:
                        raise Warning(_('Can\'t retrieve lot on stock'))
        return move

    @api.model
    def _check_move_state(self, line):
        if line.lot_id:
            move = self.get_move_from_line(line)
            if move.state == 'confirmed':
                move.action_assign()
                move.refresh()
            if move.state != 'assigned':
                raise Warning(_('Can\'t reserve products for lot %s') %
                              line.lot_id.name)
        return True

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for line in self.order_line:
            self._check_move_state(line)
        return res
