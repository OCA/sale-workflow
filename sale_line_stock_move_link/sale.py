# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Chafique Delli
#    Copyright 2014 Akretion SA
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

from openerp.osv import orm, fields


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    _columns = {
        'line_parent_id': fields.many2one('sale.order.line', 'Parent Line'),
        'line_child_ids': fields.one2many('sale.order.line', 'line_parent_id',
                                          'Children Line'),
        }


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = {'order_line': False}
        new_order_id = super(SaleOrder, self).copy(cr, uid, id,
                                                   default=default,
                                                   context=context)
        order_line_model = self.pool.get('sale.order.line')
        order = self.browse(cr, uid, id, context=context)
        for origin_order_line in order.order_line:
            if not origin_order_line.line_parent_id:
                default = {
                    'order_id': new_order_id,
                    'line_child_ids': False,
                }
                new_order_line_id = order_line_model.copy(
                    cr, uid, origin_order_line.id,
                    default=default, context=context)
            for child_line in origin_order_line.line_child_ids:
                default = {
                    'line_parent_id': new_order_line_id,
                    'order_id': new_order_id,
                    }
                order_line_model.copy(cr, uid, child_line.id,
                                      default=default, context=context)
        return new_order_id
