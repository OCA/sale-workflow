# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2014 Camptocamp SA
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


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def _get_last_sale_sums(self, cr, uid, last_lines, context=None):
        """ Get last price from sale order lines

        If multiple lines exists at the same date we do an average
        """
        if len(last_lines) == 1:
            return last_lines[0].price_unit, last_lines[0].product_uom_qty
        else:
            sum_price = 0.0
            sum_qty = 0.0
            for line in last_lines:
                sum_qty += line.product_uom_qty
                sum_price += line.price_unit * line.product_uom_qty
            if sum_qty == 0:
                return 0
            return sum_price / float(sum_qty), sum_qty

    def _get_last_sale(self, cr, uid, ids, field_name, arg, context=None):
        """ Get last sale price and last sale date
        """
        res = {}
        for res_id in ids:
            res[res_id] = {'last_sale_price': False,
                           'last_sale_qty': False,
                           'last_sale_date': False}
        for line in self.browse(cr, uid, ids, context=context):
            if not line.product_id:
                continue

            line_ids = self.search(
                cr, uid,
                [('order_partner_id', '=', line.order_partner_id.id),
                 ('product_id', '=', line.product_id.id),
                 ('state', 'in', ['confirmed', 'done'])],
                context=context)

            if not line_ids:
                continue

            old_lines = self.browse(cr, uid, line_ids, context=context)
            old_lines.sort(key=lambda l: l.order_id.date_order, reverse=True)

            last_date = old_lines[0].order_id.date_order
            last_lines = [l for l in old_lines
                          if l.order_id.date_order == last_date]
            res[line.id]['last_sale_date'] = last_date

            (last_price, last_qty) = self._get_last_sale_sums(
                cr, uid, last_lines, context=context)
            res[line.id]['last_sale_price'] = last_price
            res[line.id]['last_sale_qty'] = last_qty
        return res

    _columns = {
        'last_sale_price': fields.function(
            _get_last_sale,
            type="float",
            string='Last Sale Price',
            multi='last_sale'),
        'last_sale_qty': fields.function(
            _get_last_sale,
            type="float",
            string='Last Sale Quantity',
            multi='last_sale'),
        'last_sale_date': fields.function(
            _get_last_sale,
            type="date",
            string='Last Sale Date',
            multi='last_sale'),
    }
