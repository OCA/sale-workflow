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
from openerp.osv import orm, fields


class PurchaseOrderSortingWizard(orm.TransientModel):
    _name = 'purchase.order.sorting.wizard'

    # note: each sort key needs an associated lambda function
    # in PurchaseOrderSorting.sort_order_lines()
    sort_keys = [
        ('name', 'Name'),
        ('description', 'Description'),
        ('quantity', 'Quantity'),
    ]

    sort_dirs = [
        ('ascending', 'ascending'),
        ('descending', 'descending'),
    ]

    _columns = {
        'key1': fields.selection(sort_keys, 'First by', required=False),
        'dir1': fields.selection(sort_dirs, 'direction', required=True),
        'key2': fields.selection(sort_keys, 'Then by', required=False),
        'dir2': fields.selection(sort_dirs, 'direction', required=True),
    }

    last_key1 = None
    last_dir1 = 'ascending'
    last_key2 = None
    last_dir2 = 'ascending'

    _defaults = {
        'key1': lambda s, cr, uid, c: PurchaseOrderSortingWizard.last_key1,
        'dir1': lambda s, cr, uid, c: PurchaseOrderSortingWizard.last_dir1,
        'key2': lambda s, cr, uid, c: PurchaseOrderSortingWizard.last_key2,
        'dir2': lambda s, cr, uid, c: PurchaseOrderSortingWizard.last_dir2,
    }

    def do_sort(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        po_ids = context.get('active_ids')
        if po_ids is None:
            return
        assert len(ids) == 1,\
            'Exactly one set of sorting options can be used at a time.'
        wiz = self.browse(cr, uid, ids, context=context)[0]

        PurchaseOrderSortingWizard.last_key1 = wiz.key1
        PurchaseOrderSortingWizard.last_dir1 = wiz.dir1
        PurchaseOrderSortingWizard.last_key2 = wiz.key2
        PurchaseOrderSortingWizard.last_dir2 = wiz.dir2

        self.pool['purchase.order'].do_sort(cr, uid, po_ids, [
            {'key': wiz.key1, 'dir': wiz.dir1},
            {'key': wiz.key2, 'dir': wiz.dir2},
        ], context=context)
        return {'type': 'ir.actions.act_window_close'}
