# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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
#

import decimal_precision as dp

from operator import add
from osv import osv, fields


class account_invoice(osv.osv):

    _inherit = "account.invoice"

    def _special_lines(self, cr, uid, ids, name, args, context=None):
        """ Compute Discount and Advances amounts (sum of all the products of
        these types)
        """
        res = {}
        # mapping where keys are product special type and values are the
        # invoice fields
        product_to_fields = {'discount': 'extra_discount_amount',
                             'advance': 'advance_amount',
                             'delivery': 'delivery_amount'}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = dict((field, 0.0)
                                   for field in product_to_fields.values())
            for special_type, field in product_to_fields.iteritems():
                res[invoice.id][field] = reduce(
                    add,
                    [
                        line.price_subtotal
                        for line in invoice.invoice_line
                        if line.product_id and
                        line.product_id.special_type == special_type
                    ], 0.0)
        return res

    # super does not work for store function triggers as self is not the
    # current object
    # we have to redefine the method in this class
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get(
            'account.invoice.line'
        ).browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    _columns = {
        'extra_discount_amount': fields.function(
            _special_lines,
            method=True,
            digits_compute=dp.get_precision('Account'),
            string='Extra Discount',
            multi='special_lines',
            store={
                'account.invoice': (
                    lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20
                    ),
                'account.invoice.line': (_get_invoice_line, [
                    'price_unit', 'invoice_line_tax_id', 'quantity',
                    'discount', 'invoice_id', 'product_id'
                    ], 20),
            }),
        'advance_amount': fields.function(
            _special_lines,
            method=True,
            digits_compute=dp.get_precision('Account'),
            string='Advance',
            multi='special_lines',
            store={
                'account.invoice': (
                    lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20
                    ),
                'account.invoice.line': (_get_invoice_line, [
                    'price_unit', 'invoice_line_tax_id', 'quantity',
                    'discount', 'invoice_id', 'product_id'
                    ], 20),
            }),
        'delivery_amount': fields.function(
            _special_lines,
            method=True,
            digits_compute=dp.get_precision('Account'),
            string='Delivery Costs',
            multi='special_lines',
            store={
                'account.invoice': (
                    lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20
                    ),
                'account.invoice.line': (_get_invoice_line, [
                    'price_unit', 'invoice_line_tax_id', 'quantity',
                    'discount', 'invoice_id', 'product_id'
                    ], 20),
            }),
    }

account_invoice()


class account_invoice_line(osv.osv):

    _inherit = "account.invoice.line"

    def _hidden_in_report(self, cr, uid, ids, name, args, context=None):
        """
        Discount and Advances are hidden in the report template and displayed
        as a sum in the totals
        """
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = False
            if line.product_id and line.product_id.special_type in (
                'discount', 'advance', 'delivery'
            ):
                res[line.id] = True
        return res

    _columns = {
        'hide_in_report': fields.function(_hidden_in_report,
                                          method=True,
                                          string='Hide the line in reports',
                                          type="boolean",
                                          store=True)}

account_invoice_line()
