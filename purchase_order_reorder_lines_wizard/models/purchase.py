# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 initOS GmbH (<http://www.initos.com>).
#    Author Andreas Zoellner <andreas.zoellner at initos.com>
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


class PurchaseOrderLine(orm.Model):
    _inherit = 'purchase.order.line'

    # max. 'sequence' of current order's lines, set by on_change_order_line()
    max_sequence = 0

    def _get_sequence_default(self, cr, uid, context=None):
        return (PurchaseOrderLine.max_sequence or 0) + 1

    _defaults = {
        'sequence': _get_sequence_default,
    }


class PurchaseOrder(orm.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'

    def ask_ordering(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return True
        view_ref = self.pool['ir.model.data'].get_object_reference(
            cr, uid,
            'purchase_order_reorder_lines_wizard',
            'purchase_order_sorting_wizard'
        )
        view_id = view_ref and view_ref[1] or False
        # create wizard
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sorting options',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': view_id,
            'res_model': 'purchase.order.sorting.wizard',
            'nodestroy': True,
            'target': 'new',
            'context': context,
        }

    @staticmethod
    def sort_order_lines(order_lines, sort_option):
        key = sort_option['key']
        dir = sort_option['dir']

        if key == 'name':
            fun = lambda x: x.product_id.name
        elif key == 'description':
            fun = lambda x: x.name
        elif key == 'quantity':
            fun = lambda x: x.product_qty
        else:
            # possibly default: sort by generated purchase.order.line's ID
            # fun = lambda x: x.id
            return order_lines

        return sorted(order_lines, key=fun, reverse=(dir == 'descending'))

    def do_sort(self, cr, uid, ids, sort_options, context=None):
        """Sort order lines according to sorting wizard."""
        for order in self.browse(cr, uid, ids, context=context):
            # Starting with Python 2.2, sorts are guaranteed to be stable.
            # This is required here in order to apply multiple sort options.
            order_lines = order.order_line
            for sort_option in reversed(sort_options):
                order_lines = self.sort_order_lines(order_lines, sort_option)
            purchase_order_line_obj = self.pool['purchase.order.line']
            for index, line in enumerate(order_lines):
                # set 1-based sorting index
                purchase_order_line_obj.write(
                    cr, uid, line.id, {'sequence': index + 1}, context=context
                )
        return True

    def on_change_order_line(self, cr, uid, ids, order_lines, context=None):
        # determine current max. sequence of order_lines
        max_seq = 0
        for line in order_lines:
            line_id = line[1]
            if line_id:
                # currently stored value
                line_rec = self.pool['purchase.order.line'].browse(
                    cr, uid, line_id, context=context
                )
                if line_rec and line_rec.sequence:
                    max_seq = max(max_seq, line_rec.sequence)
            vals = line[2]
            if vals and vals.get('sequence'):
                # added or changed value
                max_seq = max(max_seq, vals.get('sequence'))
        # hand over to PurchaseOrderLine
        PurchaseOrderLine.max_sequence = max_seq
        return True
