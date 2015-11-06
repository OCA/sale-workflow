# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 credativ ltd (<http://www.credativ.co.uk>).
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

from openerp.osv import osv


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def product_id_change(
        self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0,
        uos=False, name='', partner_id=False, lang=False, update_tax=True,
        date_order=False, packaging=False, fiscal_position=False, flag=False,
        context=None
    ):

        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context
        )

        if product and pricelist:
            value = res['value']
            pricelist_obj = self.pool.get('product.pricelist')
            pricelist_item_obj = self.pool.get('product.pricelist.item')
            list_price = pricelist_obj.price_rule_get(
                cr, uid, [pricelist], product, qty or 1.0,
                partner_id, context=context
            )
            rule_id = (list_price.get(pricelist) and
                       list_price[pricelist][1] or False)
            value['discount'] = rule_id and pricelist_item_obj.read(
                cr, uid, [rule_id], ['discount'])[0]['discount'] or 0.00

        return res
