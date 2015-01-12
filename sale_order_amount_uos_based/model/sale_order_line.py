# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
import openerp.addons.decimal_precision as dp


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = super(SaleOrderLine, self)._amount_line(
            cr, uid, ids, field_name, arg, context)
        user = self.pool.get('res.users').browse(
            cr, uid, uid, context=context)
        user_groups = [g.id for g in user.groups_id]
        group_ref = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'product', 'group_uos')
        if group_ref and group_ref[1] in user_groups:
            uom_qty_dict = {}
            for line in self.browse(cr, uid, ids, context=context):
                uom_qty_dict[line.id] = line.product_uom_qty
                # replace product_uom_qty by product_uos_qty
                cr.execute(
                    'UPDATE sale_order_line SET product_uom_qty = %s '
                    'WHERE id = %s',
                    (line.product_uos_qty, line.id)
                )
            res = super(SaleOrderLine, self)._amount_line(
                cr, uid, ids, field_name, arg, context)
            # replace product_uom_qty by the original value
            for line_id, uom_qty in uom_qty_dict.iteritems():
                cr.execute(
                    'UPDATE sale_order_line SET product_uom_qty = %s '
                    'WHERE id = %s',
                    (uom_qty, line_id)
                )
        return res

    _columns = {
        'price_subtotal': fields.function(
            _amount_line, string='Subtotal',
            digits_compute=dp.get_precision('Account')),
    }
