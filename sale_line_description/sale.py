# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2013 Agile Business Group sagl
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


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    def product_id_change(
        self, cr, uid, ids, pricelist, product_id, qty=0,
        uom=False, qty_uos=0, uos=False, name='', partner_id=False,
        lang=False, update_tax=True, date_order=False, packaging=False,
        fiscal_position=False, flag=False, context=None
    ):
        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product_id, qty=qty, uom=uom,
            qty_uos=qty_uos, uos=uos, name='', partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order,
            packaging=packaging, fiscal_position=fiscal_position,
            flag=flag, context=context
        )
        if product_id:
            user = self.pool.get('res.users').browse(
                cr, uid, uid, context=context)
            user_groups = [g.id for g in user.groups_id]
            ref = self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'sale_line_description',
                'group_use_product_description_per_so_line'
            )
            if ref and len(ref) > 1 and ref[1] and not flag:
                group_id = ref[1]
                if group_id in user_groups:
                    product_obj = self.pool.get('product.product')
                    product = product_obj.browse(
                        cr, uid, product_id, context=context)
                    if (
                        product and
                        product.description and
                        'value' in res
                    ):
                        res['value']['name'] = product.description_sale
        return res
