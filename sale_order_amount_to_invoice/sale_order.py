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
import operator


def get_operator(name):
    """
    Return an operator as function.

    The operators are used to calculate the domains and
    match the python operators.

    lesser than:     <
    lesser or equal: <=
    bigger than:     >
    bigger or equal: >=
    different:       <> or !=
    equal:           = or ==
    """
    if name == '<':
        return operator.lt
    elif name == '<=':
        return operator.le
    elif name == '>':
        return operator.gt
    elif name == '>=':
        return operator.ge
    elif name == '!=' or name == '<>':
        return operator.ne
    elif name == '=' or name == '==':
        return operator.eq


class SaleOrder(orm.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def _amount_to_invoice(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            invoiced_amount = sum(
                invoice.amount_total
                for invoice in sale.invoice_ids
                if invoice.state in ('open', 'paid')
            )
            res[sale.id] = max(0.0, sale.amount_total - invoiced_amount)
        return res

    def _amount_to_invoice_search(self, cr, uid, obj, name, args,
                                  context=None):
        """Amount to invoice filter"""

        if context is None:
            context = {}

        amount_to_invoice = None
        compare = None

        for arg in args:
            if arg[0] == 'amount_to_invoice':
                amount_to_invoice = arg[2]
                compare = get_operator(arg[1])
                break

        if amount_to_invoice is not None and compare:
            super_search = super(SaleOrder, self).search
            all_ids = super_search(cr, uid, [], context=context)
            search_ids = []

            for sale in self.browse(cr, uid, all_ids, context=context):
                if compare(sale.amount_to_invoice, amount_to_invoice):
                    search_ids.append(sale.id)

            return [('id', 'in', search_ids)]

        return []

    _columns = {
        'amount_to_invoice': fields.function(
            _amount_to_invoice, fnct_search=_amount_to_invoice_search,
            string='Amount to Invoice', type='float'),
    }
