# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Tax Included Excluded module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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


class price_type(orm.Model):
    _inherit = 'product.price.type'

    _columns = {
        'price_include_taxes': fields.boolean('Price Include Taxes'),
        }


class product_template(orm.Model):
    _inherit = 'product.template'

    def _mass_convert_price_include_excluded_tax(
            self, cr, uid, data, way, context=None):
        assert way in ('i2e', 'e2i'), 'way can only be i2e or e2i'
        if data:
            products = self.pool['product.product'].browse(
                cr, uid, data.keys(), context=context)
            for product in products:
                if product.taxes_id:
                    taxres = self.pool['account.tax'].compute_all(
                        cr, uid, product.taxes_id, data[product.id], 1)
                    if way == 'i2e':
                        data[product.id] = taxres['total']
                    elif way == 'e2i':
                        data[product.id] = taxres['total_included']
        return

    def _price_get(self, cr, uid, products, ptype='list_price', context=None):
        if context is None:
            context = {}
        res = super(product_template, self)._price_get(
            cr, uid, products, ptype=ptype, context=context)
        if context.get('fiscal_position_id') and res:
            priceto = self.pool['product.price.type']
            fp = self.pool['account.fiscal.position'].browse(
                cr, uid, context.get('fiscal_position_id'), context=context)
            pricet_ids = priceto.search(
                cr, uid, [('field', '=', ptype)], context=context)
            assert pricet_ids, 'Missing product.price.type'
            pricet = priceto.browse(cr, uid, pricet_ids[0], context=context)
            if fp.price_include_taxes != pricet.price_include_taxes:
                if pricet.price_include_taxes:
                    self._mass_convert_price_include_excluded_tax(
                        cr, uid, res, 'i2e', context=context)
                else:
                    self._mass_convert_price_include_excluded_tax(
                        cr, uid, res, 'e2i', context=context)
        return res
