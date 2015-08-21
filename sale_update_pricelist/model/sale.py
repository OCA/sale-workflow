# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Hugo Santos
#    Copyright 2015 FactorLibre
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
from openerp import models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines,
                              context=None):
        context = context or {}
        if not pricelist_id:
            return {}
        pricelist = self.pool.get('product.pricelist').browse(
            cr, uid, pricelist_id, context=context)
        res = {'value': {}}
        res['value']['currency_id'] = pricelist.currency_id.id
        if not order_lines or order_lines == [(6, 0, [])]:
            return res
        line_dict = self.resolve_2many_commands(
            cr, uid, 'order_line', order_lines, context=context)
        warning_msg = ""
        for line in line_dict:
            # Reformat line_dict so as to be compatible with what is
            # accepted in res['value']
            for key, value in line.iteritems():
                if isinstance(value, tuple) and len(value) == 2:
                    line[key] = value[0]
            if line.get('product_id'):
                price = self.pool.get('product.pricelist').price_get(
                    cr, uid, [pricelist_id], line['product_id'],
                    line['product_uom_qty'] or 1.0, False,
                    {'uom': line['product_uom']})[pricelist_id]
                if price:
                    line['price_unit'] = price
                else:
                    warning_msg += _(
                        "Cannot find a pricelist line matching product %s"
                        " and quantity %s. "
                        "Price will remaing unchanged\n") % (
                        line['name'], line['product_uom_qty'])

        res['value']['order_line'] = line_dict
        if warning_msg:
            res['warning'] = {
                'title': _('Pricelist Warning!'),
                'message': warning_msg
            }
        return res
