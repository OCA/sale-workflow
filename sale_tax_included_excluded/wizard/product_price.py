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


class product_price_list(orm.TransientModel):
    _inherit = 'product.price_list'

    _columns = {
        'pricelist_type': fields.related(
            'price_list', 'type', type='char', string='Pricelist Type'),
        'fiscal_position_id': fields.many2one(
            'account.fiscal.position', 'Fiscal Position'),
        }

    def price_list_change(self, cr, uid, ids, price_list, context=None):
        res = {'value': {}}
        if price_list:
            pricelist = self.pool['product.pricelist'].browse(
                cr, uid, price_list, context=context)
            res['value']['pricelist_type'] = pricelist.type
        return res

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wiz = self.browse(cr, uid, ids[0], context=context)
        wizctx = context.copy()
        if wiz.pricelist_type == 'sale' and wiz.fiscal_position_id:
            wizctx['fiscal_position_id'] = wiz.fiscal_position_id.id
        return super(product_price_list, self).print_report(
            cr, uid, ids, context=wizctx)
