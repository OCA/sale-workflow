# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _

class sale_order(orm.Model):
    _inherit = 'sale.order'
    
    def _get_search_vals_for_quantity(self, cr, uid, line, context=None):
        return [
            ('order_id', '=', line.order_id.id),
            ('state', '!=', 'cancel'),
            ('product_id.categ_id', '=', line.product_id.categ_id.id),
        ]
    
    def _get_quantity_to_compute(self, cr, uid, line, context=None):
        if context is None:
            context = {}
        quantity = line.product_uom_qty
        if line.product_id:
            order_line_obj = self.pool.get('sale.order.line')
            search_vals = self._get_search_vals_for_quantity(cr, uid, line, context=context)
            line_ids = order_line_obj.search(cr, uid, search_vals, context=context)
            quantity = reduce(lambda x,y: x+y,
                [z.product_uom_qty for z
                in order_line_obj.browse(cr, uid, line_ids, context=context)], 0)
        return quantity
    
    def _get_price_of_line(self, cr, uid, product_id,
                           qty, partner_id, pricelist_id,
                           context=None):
        if context is None:
            context = {}
        price_list_obj = self.pool.get('product.pricelist')
        res = price_list_obj.price_get_multi(cr, uid,
            pricelist_ids=[pricelist_id],
            products_by_qty_by_partner=[(product_id, qty, partner_id)],
            context=context)
        return res
    
    def _check_if_edit(self, cr, uid, res, context=None):
        if context is None:
            context = {}
        price_list_item_obj = self.pool.get('product.pricelist.item')
        if res.get('item_id'):
            item_id = res.get('item_id', False)
            if item_id:
                item = price_list_item_obj.browse(cr, uid, item_id, context=context)
                if item.categ_id:
                    return True
        return False
    
    def _get_child_pricelist(self, cr, uid, res, context=None):
        if context is None:
            context = {}
        price_list_item_obj = self.pool.get('product.pricelist.item')
        if res.get('item_id'):
            item_id = res.get('item_id', False)
            if item_id:
                item = price_list_item_obj.browse(cr, uid, item_id, context=context)
                if item.base_pricelist_id:
                    return item.base_pricelist_id.id
        return False
    
    def compute_global_discount(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        order_line_obj = self.pool.get('sale.order.line')
        for sale in self.browse(cr, uid, ids, context=context):
            if sale.state in ('draft','sent'):
                line_ids = [x.id for x in sale.order_line]
                order_line_obj.compute_global_discount(cr, uid, line_ids, context=context)
        return True

class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def compute_global_discount(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        price_list_obj = self.pool.get('product.pricelist')
        order_obj = self.pool.get('sale.order')
        for line in self.browse(cr, uid, ids, context=context):
            sale = line.order_id
            context['date'] = sale.date_order
            partner_id = sale.partner_id.id
            if line.product_id:
                pricelist_id = sale.pricelist_id.id
                product_id = line.product_id.id
                qty = order_obj._get_quantity_to_compute(cr, uid, line, context=context)
                if qty:
                    res = order_obj._get_price_of_line(cr, uid, product_id,
                        qty, partner_id, pricelist_id, context=context)
                    while True:
                        new_pricelist_id = order_obj._get_child_pricelist(cr, uid,
                                                                     res, context=context)
                        if not new_pricelist_id:
                            break
                        res = order_obj._get_price_of_line(cr, uid, product_id,
                            qty, partner_id, new_pricelist_id, context=context)
                        pricelist_id = new_pricelist_id
                    price_unit = False
                    if order_obj._check_if_edit(cr, uid, res, context=context):
                        price_unit = res.get(line.product_id.id, {}).get(pricelist_id, False)
                    else:
                        price_unit = price_list_obj.price_get(cr, uid,
                            [pricelist_id], product_id, line.product_uom_qty,
                            partner=sale.partner_id.id, context=context)[pricelist_id]
                    if price_unit is not False:
                        self.write(cr, uid,
                                   line.id, {'price_unit': price_unit},
                                   context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
