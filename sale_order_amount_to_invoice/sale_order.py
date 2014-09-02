# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp.osv import fields, orm


class SaleOrder(orm.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def _amount_to_invoice(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            invoiced_amount = sum(
                invoice.amount_total
                for invoice in sale.invoice_ids
                if invoice.state in ('open', 'done')
            )
            res[sale.id] = max(0.0, sale.amount_total - invoiced_amount)
        return res

    def _amount_to_invoice_search(self, cr, uid, obj, name, args, context=None):
        """Account root filter"""

        if context is None:
            context = {}

        amount_to_invoice = None

        for arg in args:
            if arg[0] == 'amount_to_invoice':
                amount_to_invoice = arg[2]
                break

        if amount_to_invoice is not None:
            super_search = super(SaleOrder, self).search
            all_ids = super_search(cr, uid, [],
                                   context=context)
            search_ids = []

            for sale in self.browse(cr, uid, all_ids, context=context):
                if sale.amount_to_invoice != 0.00:
                    search_ids.append(sale.id)
            return [('id', 'in', search_ids)]

        return []

    _columns = {
        'amount_to_invoice': fields.function(
            _amount_to_invoice, fnct_search=_amount_to_invoice_search,
            string='Amount to Invoice', type='float'),
    }
