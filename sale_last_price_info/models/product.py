# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_last_sale(self):
        """
        Get last sale price, last sale date and last customer
        """
        sale_line_obj = self.env['sale.order.line']
        for product in self:
            last_date = False
            last_price = False
            last_customer = False
            lines = sale_line_obj.search(
                [('product_id', '=', product.id),
                 ('state', 'in', ['confirmed', 'done'])])
            if lines:
                old_lines = sorted(lines, key=lambda l: l.order_id.date_order,
                                   reverse=True)
                last_date = old_lines[0].order_id.date_order
                last_price = old_lines[0].price_unit
                last_customer = old_lines[0].order_id.partner_id

            product.last_sale_date = last_date
            product.last_sale_price = last_price
            product.last_customer = last_customer

    last_sale_price = fields.Float(
        string='Last Sale Price', compute=_get_last_sale)
    last_sale_date = fields.Date(
        string='Last Sale Date', compute=_get_last_sale)
    last_customer = fields.Many2one(
        comodel_name='res.partner', string='Last Customer',
        compute=_get_last_sale)
