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


class AccountInvoiceLine(orm.Model):
    _inherit = 'account.invoice.line'
    _order = 'sale_parent_line_id, name desc'

    def _get_invoice_line_from_order_line(self, cr, uid, ids, context=None):
        invoice_line_ids = self.pool['account.invoice.line'].search(
            cr, uid, [('sale_line_id', 'in', ids)], context=context)
        return invoice_line_ids

    _columns = {
        'sale_line_id': fields.many2one(
            'sale.order.line',
            'Sales Order Line',
            ondelete='set null',
            select=True,
            readonly=True),
        'sale_parent_line_id': fields.related(
            'sale_line_id',
            'line_parent_id',
            type='many2one',
            relation='sale.order.line',
            string='Parent Product',
            store={
                'account.invoice.line': (
                    lambda self, cr, uid, ids, c=None: ids,
                    ['sale_line_id'],
                    10),
                'sale.order.line': (
                    _get_invoice_line_from_order_line,
                    ['line_parent_id'],
                    20)
            }
        )
    }
