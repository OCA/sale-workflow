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

    @api.onchange(
        'property_ids', 'product_id', 'product_uos_qty'
    )
    def quantity_property_ids_changed(self):
        prop_ctx = self.env.context.copy()
        if 'lang' in prop_ctx:
            del prop_ctx['lang']
        if self.product_id and self.property_ids and self.product_uos_qty:
            if self.product_id.quantity_formula_id:
                prop_dict = {}
                uom_precision = self.pool['decimal.precision'].precision_get(
                    self._cr, self._uid, 'Product UoS')
                for prop in self.env['mrp.property'].with_context(
                    prop_ctx
                ).browse([p.id for p in self.property_ids]):
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
                }
                try:
                    exec self.product_id.quantity_formula_id.\
                        formula_text in localdict
                    try:
                        amount = localdict['result']
                    except KeyError:
                        raise except_orm(
                            _('Error'),
                            _("Formula must contain 'result' variable"))
                    # rounding because decimal values, different from what
                    # displayed on interface, could generate infinite
                    # on_change loop
                    self.product_uom_qty = float_round(
                        amount, precision_digits=uom_precision)
                except KeyError:
                    _logger.warning(
                        "KeyError for formula '%s' and prop_dict '%s'"
                        % (self.product_id.quantity_formula_id.formula_text,
                            prop_dict))
