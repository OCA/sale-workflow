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
from openerp.exceptions import Warning as UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number', copy=False)

    @api.model
    def _select_lot_product(self, product):
        """Method inherited in the module sale_rental_lot_selection"""
        return product

    @api.model
    def _select_lot_stock_location(self, product, warehouse):
        """Method inherited in the module sale_rental_lot_selection"""
        return warehouse.lot_stock_id

    @api.multi
    def product_id_change_with_wh(
            self, pricelist, product_id, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, warehouse_id=False):
        res = super(SaleOrderLine, self).product_id_change_with_wh(
            pricelist, product_id, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag,
            warehouse_id=warehouse_id)

        product = self.env['product.product'].browse(product_id)
        warehouse = self.env['stock.warehouse'].browse(warehouse_id)
        location = self._select_lot_stock_location(product, warehouse)
        # DO NOT use 'product_id' AFTER THIS LIMIT ; only use 'product'
        product = self._select_lot_product(product)

        # Search all lot existing lot for the product and location selected
        quants = self.env['stock.quant'].read_group([
            ('product_id', '=', product.id),
            ('location_id', 'child_of', location.id),
            ('qty', '>', 0),
            ('lot_id', '!=', False),
            ], ['lot_id'], 'lot_id')
        available_lots = [quant['lot_id'][0] for quant in quants]
        res.setdefault('domain', {}).update(
            {'lot_id': [('id', 'in', available_lots)]})
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
            if p.picking_type_id.code == 'outgoing':  # required for rental
                for m in p.move_lines:
                    if line.lot_id == m.restrict_lot_id:
                        move = m
                        lot_count += 1
                        # if counter is 0 or > 1
                        # it means that something goes wrong
                        if lot_count != 1:
                            raise UserError(_("Can't retrieve lot on stock"))
        return move

    @api.model
    def _check_move_state(self, line):
        if line.lot_id:
            move = self.get_move_from_line(line)
            if move.state != 'confirmed':
                raise UserError(_("Can't reserve products for lot %s") %
                                line.lot_id.name)
            else:
                move.action_assign()
                move.refresh()
                if move.state != 'assigned':
                    raise UserError(_("Can't reserve products for lot %s") %
                                    line.lot_id.name)
        return True

    @api.model
    def action_ship_create(self):
        super(SaleOrder, self).action_ship_create()
        for line in self.order_line:
            self._check_move_state(line)
            return True
