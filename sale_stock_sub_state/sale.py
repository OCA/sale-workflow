# -*- encoding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2015 AKRETION (http://www.akretion.com)
#   @author Chafique DELLI
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm


class StockPicking(orm.Model):
    _inherit = 'stock.picking'

    def write(self, cr, uid, ids, values, context=None):
        sale_obj = self.pool['sale.order']
        stock_picking = self.browse(cr, uid, ids[0], context=context)
        status_list = ['assigned', 'done']
        if 'state' in values:
            if stock_picking.sale_id and values['state'] in status_list:
                if values['state'] == 'done':
                    sub_status = 'sent'
                else:
                    sub_status = values['state']
                sale_obj.write(cr, uid, stock_picking.sale_id.id, {
                    'sub_state': sub_status,
                }, context=context)
        return super(StockPicking, self).write(
            cr, uid, ids, values, context=context)


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def _get_sub_state_selection(self, cr, uid, context=None):
        selection = super(SaleOrder, self)._get_sub_state_selection(
            cr, uid, context=context)
        selection += [
            ('assigned', 'Started Shipment'),
            ('sent', 'Sent'),
        ]
        return selection
