# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP 
#   Copyright (C) 2011-2013 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class price_type(orm.Model):
    _inherit = 'product.price.type'

    def _price_inc_field_get(self, cr, uid, context=None):
        return self._price_field_get(cr, uid, context=context)

    _columns = {
        'field_price_inc' : fields.selection(_price_inc_field_get,
            "Product Field Tax Inc",
            size=32,
            required=True,
            help="Associated field in the product form."),
    }


class product_product(orm.Model):
    _inherit = 'product.product'

    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        if context is None:
            context = {}
        if 'tax_inc' in context:
            price_type_obj = self.pool['product.price.type']
            price_type_id = price_type_obj.search(cr, uid, ['|', 
                                        ['field_price_inc', '=', ptype],
                                        ['field', '=', ptype],
                                        ], context=context)
            price_type = price_type_obj.browse(cr, uid, price_type_id[0], context=context)
            if context['tax_inc']:
                ptype = price_type.field_price_inc
            else:
                ptype = price_type.field
        if not ptype:
            raise orm.except_orm(('USER ERROR'),
                _('The Pricelist type are not correctly configured,'
                  ' please check if "Product Field Tax Inc" is fill'
                  ' on every product type. Menu > Sale > Configuration'
                  ' > Pricelists > Price Types'))
        res = super(product_product, self).price_get(cr, uid, ids, ptype=ptype, context=context)
        return res

    _columns = {
        'list_price_tax_inc': fields.float('Sale Price Tax Inc',
            digits_compute=dp.get_precision('Product Price'),
            help=("Base price to compute the customer "
                "price. Sometimes called the catalog price.")),
    }


    #NOTA : the solution taken for computing the price is really, really simple
    #a better solution can be implemented later (like giving the posibility to
    #select the way we want to manage our catalog by default (inc or excluded)
    #you can overwrite easily the method update if you need in your own module
    #by default we always update the list_price

    def _update_price(self, cr, uid, ids, context=None):
        tax_obj = self.pool['account.tax']
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        for product in self.browse(cr, uid, ids, context=context):
            price = product.list_price_tax_inc
            taxes =  [tax.related_inc_tax_id for tax in product.taxes_id if tax.related_inc_tax_id]
            taxes = tax_obj.compute_all(cr, uid, taxes, price, 1, product=product.id)
            price_exc = taxes['total']
            ctx = context.copy()
            ctx['update_price'] = True
            self.write(cr, uid, [product.id], {'list_price': price_exc}, context=ctx)

    def create(self, cr, uid, vals, context=None):
        create_id = super(product_product, self).create(cr, uid, vals, context=context) 
        self._update_price(cr, uid, [create_id], context=context)
        return create_id

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        super(product_product, self).write(cr, uid, ids, vals, context=context)
        if not context.get('update_price'):
            self._update_price(cr, uid, ids, context=context)
        return True

