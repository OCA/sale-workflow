# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl
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

from openerp import models, api
from openerp.tools.translate import _
from openerp.exceptions import except_orm


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('property_ids', 'product_uos')
    def price_property_ids_changed(self):
        prop_dict = {}
        ctx = self.env.context.copy()
        if 'lang' in ctx:
            del ctx['lang']
        if self.product_id:
            for prop in self.env['mrp.property'].with_context(ctx).browse(
                [p.id for p in self.property_ids]
            ):
                if prop.group_id.name in prop_dict:
                    raise except_orm(
                        _('Error'),
                        _('Property of group %s already present')
                        % prop.group_id.name)
                prop_dict[prop.group_id.name] = prop.value
            ctx.update({'uos_id': self.product_uos.id,
                        'uom': self.product_uom.id,
                        'date': self.order_id.date_order,
                        'properties': prop_dict,
                        })
            self.price_unit = self.env['product.pricelist'].with_context(
                ctx).price_get(
                    self.product_id.id,
                    self.product_uom_qty or 1.0,
                    self.order_id.partner_id.id)[self.order_id.pricelist_id.id]

    def product_id_change(
        self, cr, uid, ids, pricelist, product_id, qty=0,
        uom=False, qty_uos=0, uos=False, name='', partner_id=False,
        lang=False, update_tax=True, date_order=False, packaging=False,
        fiscal_position=False, flag=False, context=None
    ):
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product_id, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context)
        if 'value' in res:
            # get empty properties
            res['value']['property_ids'] = []
            # get empty properties dynamic fields
            property_group_pool = self.pool['mrp.property.group']
            group_to_empty_ids = property_group_pool.search(
                cr, uid, [('draw_dynamically', '=', True)], context=context)
            groups = property_group_pool.browse(
                cr, uid, group_to_empty_ids, context=context
            )
            for group in groups:
                res['value'][group.field_id.name] = None
        return res
