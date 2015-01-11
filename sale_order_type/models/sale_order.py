# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#  OpenERP, Open Source Management Solution.                                 #
#                                                                            #
#  @author Carlos Sánchez Cifuentes <csanchez@grupovermon.com>               #
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.      #
#                                                                            #
##############################################################################

from openerp import api
from openerp.osv import fields, orm


class SaleOrder(orm.Model):

    _inherit = 'sale.order'

    _columns = {
        'type_id': fields.many2one('sale.order.type', 'Type', required=True),
    }

    def _get_order_type(self, cr, uid, context=None):
        type_obj = self.pool['sale.order.type']
        type_ids = type_obj.search(cr, uid, [], context=context)
        return type_ids and type_ids[0] or False

    _defaults = {'type_id': _get_order_type}

    def on_change_type_id(self, cr, uid, ids, type_id, context=None):
        if type_id:
            type_obj = self.pool['sale.order.type'].browse(
                cr, uid, [type_id], context=context)
            return {'value': {'warehouse_id': type_obj[0].warehouse_id.id}}

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            if vals.get('type_id'):
                type = self.pool['sale.order.type'].browse(
                    cr, uid, [vals['type_id']], context=context)
                if type[0].sequence_id:
                    sequence_obj = self.pool['ir.sequence']
                    vals['name'] = sequence_obj.next_by_id(
                        cr, uid, type[0].sequence_id.id)
        return super(SaleOrder, self).create(cr, uid, vals, context=context)

    @api.model
    def _prepare_invoice(self, order, line_ids):
        res = super(SaleOrder, self)._prepare_invoice(order, line_ids)
        res['journal_id'] = order.type_id.journal_id.id
        return res
