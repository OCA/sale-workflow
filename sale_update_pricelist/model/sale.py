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
from openerp import models, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def onchange_pricelist_id(self, pricelist_id, order_lines):
        if not pricelist_id:
            return {}
        pricelist_model = self.env['product.pricelist']
        res = super(SaleOrder, self).onchange_pricelist_id(pricelist_id,
                                                           order_lines)
        # Remove warning from super call
        if res.get('warning'):
            res.pop('warning', None)
        if not order_lines or order_lines == [(6, 0, [])]:
            return res
        pricelist = pricelist_model.browse(pricelist_id)
        line_dict = self.resolve_2many_commands('order_line', order_lines)
        warning_msg = ""
        for line in line_dict:
            # Reformat line_dict so as to be compatible with what is
            # accepted in res['value']
            for key, value in line.iteritems():
                if isinstance(value, tuple) and len(value) == 2:
                    line[key] = value[0]
            if line.get('product_id'):
                ctx = dict(self.env.context)
                ctx['uom'] = line['product_uom']
                price = pricelist.with_context(ctx).price_get(
                    line['product_id'],
                    line['product_uom_qty'] or 1.0)[pricelist_id]
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
