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
from openerp.tools import float_round
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

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
        if context is None:
            context = {}
        property_ids = context.get('property_ids')
        prop_ctx = context.copy()
        if 'lang' in prop_ctx:
            del prop_ctx['lang']
        if product_id and property_ids and qty_uos:
            product = self.pool['product.product'].browse(
                cr, uid, product_id, context=context)
            if product.quantity_formula_id:
                prop_dict = {}
                prop_pool = self.pool['mrp.property']
                precision_pool = self.pool['decimal.precision']
                uom_precision = precision_pool.precision_get(
                    cr, uid, 'Product UoS')
                for m2m_tup in property_ids:
                    for prop in prop_pool.browse(
                        cr, uid, m2m_tup[2], context=prop_ctx
                    ):
                        if prop.group_id.name in prop_dict:
                            raise orm.except_orm(
                                _('Error'),
                                _('Property of group %s already present')
                                % prop.group_id.name)
                        prop_dict[prop.group_id.name] = prop.value

                localdict = {
                    'self': self,
                    'cr': cr,
                    'uid': uid,
                    'properties': prop_dict,
                    'qty_uos': qty_uos,
                    'product_id': product_id,
                }
                try:
                    exec product.quantity_formula_id.formula_text in localdict
                    try:
                        amount = localdict['result']
                    except KeyError:
                        raise orm.except_orm(
                            _('Error'),
                            _("Formula must contain 'result' variable"))
                    # rounding because decimal values, different from what
                    # displayed on interface, could generate infinite
                    # on_change loop
                    res['value']['product_uom_qty'] = float_round(
                        amount, precision_digits=uom_precision)
                except KeyError:
                    _logger.warning(
                        "KeyError for formula '%s' and prop_dict '%s'"
                        % (product.quantity_formula_id.formula_text,
                            prop_dict))
        # Removing product_uos_qty is needed because it can now be used to
        # compute the real quantity. Otherwise, it would be recomputed after
        # the quantity changed. See the automated test for the use case.
        if 'value' in res and 'product_uos_qty' in res['value']:
            del res['value']['product_uos_qty']
        return res
