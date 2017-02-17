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
from openerp.tools import float_round
import logging
from openerp.exceptions import except_orm

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('property_ids', 'product_uos_qty')
    def quantity_property_ids_changed(self):
        prop_ctx = self.env.context.copy()
        if 'lang' in prop_ctx:
            del prop_ctx['lang']
        if self.product_id and (self.property_ids or self.product_uos_qty):
            if self.product_id.quantity_formula_id:
                prop_dict = {}
                uom_precision = self.pool['decimal.precision'].precision_get(
                    self._cr, self._uid, 'Product UoS')
                for prop in self.env['mrp.property'].with_context(
                    prop_ctx
                ).browse(self.property_ids.ids):
                    if prop.group_id.name in prop_dict:
                        raise except_orm(
                            _('Error'),
                            _('Property of group %s already present')
                            % prop.group_id.name)
                    prop_dict[prop.group_id.name] = prop.value

                localdict = {
                    'self': self,
                    'cr': self._cr,
                    'uid': self._uid,
                    'properties': prop_dict,
                    'qty_uos': self.product_uos_qty,
                    'product_id': self.product_id.id,
                    'uos_id': self.product_uos.id,
                }
                try:
                    result = {}
                    amount = self.product_id.quantity_formula_id.\
                        compute_formula(localdict)
                    # rounding because decimal values, different from what
                    # displayed on interface, could generate infinite
                    # on_change loop
                    self.product_uom_qty = float_round(
                        amount, precision_digits=uom_precision)
                except ValueError as e:
                    message = (
                        _("Evaluation error in formula %s: ")
                        % self.product_id.quantity_formula_id.name)
                    message += e.message
                    result['warning'] = {'title': _('Warning'),
                                         'message': message}
                return result

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
            for group in property_group_pool.browse(
                    cr, uid, group_to_empty_ids, context=context
            ):
                res['value'][group.field_id.name] = None
        # Removing product_uos_qty is needed because it can now be used to
        # compute the real quantity. Otherwise, it would be recomputed after
        # the quantity changed. See the automated test for the use case.
        if 'value' in res and 'product_uos_qty' in res['value']:
            del res['value']['product_uos_qty']
        return res
