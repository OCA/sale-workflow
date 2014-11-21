# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl
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
##############################################################################

from openerp.osv import orm
from openerp.tools.translate import _


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def product_id_change(
        self, cr, uid, ids, pricelist, product, qty=0,
        uom=False, qty_uos=0, uos=False, name='', partner_id=False,
        lang=False, update_tax=True, date_order=False, packaging=False,
        fiscal_position=False, flag=False, context=None
    ):
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context)
        if context is None:
            context = {}
        properties = context.get('property_ids')
        prop_ctx = context.copy()
        if 'lang' in prop_ctx:
            del prop_ctx['lang']
        if properties and product:
            prop_dict = {}
            prop_pool = self.pool['mrp.property']
            for m2m_tup in properties:
                for prop in prop_pool.browse(
                    cr, uid, m2m_tup[2], context=prop_ctx
                ):
                    if prop.group_id.name in prop_dict:
                        raise orm.except_orm(
                            _('Error'),
                            _('Property of group %s already present')
                            % prop.group_id.name)
                    prop_dict[prop.group_id.name] = prop.value
            price = self.pool.get('product.pricelist').price_get(
                cr, uid, [pricelist],
                product, qty or 1.0, partner_id, {
                    'uom': uom or res.get('product_uom'),
                    'date': date_order,
                    'properties': prop_dict,
                })[pricelist]
            res['value']['price_unit'] = price
        return res
