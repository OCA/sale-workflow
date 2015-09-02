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

    @api.v7
    def product_id_change_with_wh(
            self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, warehouse_id=False,
            context=False):
        res = super(SaleOrderLine, self).product_id_change_with_wh(
            cr, uid, ids, pricelist, product, qty, uom,
            qty_uos, uos, name, partner_id, lang, update_tax,
            date_order, packaging, fiscal_position, flag,
            warehouse_id, context)

        available_lots = []
        lot_model = self.pool['stock.production.lot']
        product_model = self.pool['product.product']
        location = self.pool.get('stock.warehouse').browse(
            cr, uid, warehouse_id).lot_stock_id
        lot_ids = lot_model.search(
            cr, uid, [('product_id', '=', product)], context=context)
        for lot_id in lot_ids:
            # for the selected product, search for every associated lot
            # for every lot, check if it is available (in location.id)
            # if it is, add it to selectable lots
            ctx = context.copy()
            ctx['lot_id'] = lot_id
            ctx['location'] = location.id
            qty_res = product_model._product_available(
                cr, uid, [product], field_names=None, arg=False, context=ctx)
            if qty_res[product]['qty_available'] > 0:
                if lot_id not in available_lots:
                    available_lots.append(lot_id)
        res.update({'domain': {'lot_id': [('id', 'in', available_lots)]}})
        res['value']['lot_id'] = False
        return res


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res = super(
            SaleOrder, self)._prepare_order_line_procurement(
                order, line, group_id)
        res['lot_id'] = line.lot_id.id
        return res

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
            if move.state != 'confirmed':
                raise Warning(_('Can\'t reserve products for lot %s') %
                              line.lot_id.name)
            else:
                move.action_assign()
                move.refresh()
                if move.state != 'assigned':
                    raise Warning(_('Can\'t reserve products for lot %s') %
                                  line.lot_id.name)
        return True

    @api.model
    def action_ship_create(self):
        super(SaleOrder, self).action_ship_create()
        for line in self.order_line:
            self._check_move_state(line)
            return True
