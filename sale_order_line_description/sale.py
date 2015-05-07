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

from openerp.osv import orm


class SaleOrderLine(orm.Model):
    _inherit = "sale.order.line"

    def product_id_change(
        self, cr, uid, ids, pricelist, product, qty=0,
        uom=False, qty_uos=0, uos=False, name='', partner_id=False,
        lang=False, update_tax=True, date_order=False, packaging=False,
        fiscal_position=False, flag=False, context=None
    ):
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name='', partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, context=context
        )
        if product:
            if self.user_has_groups(
                    cr, uid,
                    'sale_order_line_description.'
                    'group_use_product_description_per_so_line',
                    context=context
            ):
                product = self.pool['product.product'].browse(
                    cr, uid, product, context=context)
                if product.description_sale:
                    if 'value' not in res:
                        res['value'] = {}
                    res['value']['name'] = product.description_sale
        return res
