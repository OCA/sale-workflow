# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2013-15 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def product_id_change(
        self, pricelist, product, qty=0, uom=False,
        qty_uos=0, uos=False,
        name='', partner_id=False, lang=False, update_tax=True,
        date_order=False, packaging=False, fiscal_position=False,
            flag=False):
        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging,
            fiscal_position, flag)
        if product:
            product_obj = self.env['product.product']
            if self.user_has_groups(
                    'sale_order_line_description.'
                    'group_use_product_description_per_so_line'):
                product = product_obj.browse(product)
                if product.description_sale:
                    if 'value' not in res:
                        res['value'] = {}
                    res['value']['name'] = product.description_sale
        return res
