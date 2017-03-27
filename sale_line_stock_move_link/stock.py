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


class StockMove(orm.Model):
    _inherit = 'stock.move'
    _order = 'sale_parent_line_id desc'

    def _get_move_from_order_line(self, cr, uid, ids, context=None):
        move_ids = self.pool['stock.move'].search(
            cr, uid, [('sale_line_id', 'in', ids)], context=context)
        return move_ids

    _columns = {
        'sale_parent_line_id': fields.related(
            'sale_line_id',
            'line_parent_id',
            type='many2one',
            relation='sale.order.line',
            string='Parent Product',
            store={
                'stock.move': (
                    lambda self, cr, uid, ids, c=None: ids,
                    ['sale_line_id'],
                    10),
                'sale.order.line': (
                    _get_move_from_order_line,
                    ['line_parent_id'],
                    20)
            }
        )
    }
