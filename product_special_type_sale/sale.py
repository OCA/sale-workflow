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


class sale_order(osv.osv):

    _inherit = 'sale.order'

    def _special_lines(self, cr, uid, ids, name, args, context=None):
        """ Compute Discount and Advances amounts (sum of all the products of
        these types)
        """
        res = {}
        product_to_fields = {'discount': 'extra_discount_amount',
                             'advance': 'advance_amount',
                             'delivery': 'delivery_amount'}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = dict((field, 0.0)
                                 for field in product_to_fields.values())
            for special_type, field in product_to_fields.iteritems():
                res[order.id][field] = reduce(
                    add, [
                        line.price_subtotal for line in order.order_line
                        if line.product_id and
                        line.product_id.special_type == special_type
                    ], 0.0)

        return res

    # super does not work for store function triggers as self is not the
    # current object
    # we have to redefine the methods in this class
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(
            cr, uid, ids, context=context
        ):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'extra_discount_amount': fields.function(
            _special_lines, method=True,
            digits_compute=dp.get_precision(
                'Product Price'),
            string='Extra-Discount',
            help="The amount of extra-discount",
            multi='special_lines',
            store={
                'sale.order': (
                    lambda self, cr, uid, ids, c=None: ids, ['order_line'], 10
                ),
                'sale.order.line': (_get_order, [
                    'price_unit', 'tax_id', 'discount',
                    'product_uom_qty', 'product_id'
                ], 10),
            }),
        'advance_amount': fields.function(
            _special_lines, method=True,
            digits_compute=dp.get_precision(
                'Product Price'),
            string='Advance',
            help="The amount of advances",
            multi='special_lines',
            store={
                'sale.order': (
                    lambda self, cr, uid, ids, c=None: ids, ['order_line'], 10
                ),
                'sale.order.line': (_get_order, [
                    'price_unit', 'tax_id', 'discount',
                    'product_uom_qty', 'product_id'
                ], 10),
            }),
        'delivery_amount': fields.function(
            _special_lines, method=True,
            digits_compute=dp.get_precision(
                'Product Price'),
            string='Delivery Costs',
            help="The amount of delivery costs",
            multi='special_lines',
            store={
                'sale.order': (
                    lambda self, cr, uid, ids, c=None: ids, ['order_line'], 10
                ),
                'sale.order.line': (_get_order, [
                    'price_unit', 'tax_id', 'discount',
                    'product_uom_qty', 'product_id'
                ], 10),
            }),
    }

sale_order()


class sale_order_line(osv.osv):

    _inherit = 'sale.order.line'

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
                                          type="boolean",)
    }

sale_order_line()
