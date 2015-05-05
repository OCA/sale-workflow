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

from openerp.osv import orm, fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(orm.Model):
    _inherit = "product.product"

    _columns = {
        'price_formula_id': fields.many2one(
            'mrp.property.formula', 'Price formula',
            help="You can use the variables\n"
                 " - self\n"
                 " - cr\n"
                 " - uid\n"
                 " - ptype\n"
                 " - product_id\n"
                 " - properties (dictionary of properties)\n"
                 "You have to put the result in the 'result' variable"),
    }

    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        if context is None:
            context = {}
        if 'properties' in context:
            res = {}
            for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
                res[product.id] = super(ProductProduct, self).price_get(
                    cr, uid, [product.id], ptype=ptype, context=context
                )[product.id]
                if product.price_formula_id:
                    localdict = {
                        'self': self,
                        'cr': cr,
                        'uid': uid,
                        'ptype': ptype,
                        'product_id': product.id,
                        'properties': context['properties'],
                    }
                    try:
                        exec product.price_formula_id.formula_text in localdict
                    except KeyError:
                        _logger.warning(
                            "KeyError for formula '%s' and prop_dict '%s'"
                            % (product.price_formula_id.formula_text,
                                context['properties']))
                        continue
                    try:
                        amount = localdict['result']
                    except KeyError:
                        raise orm.except_orm(
                            _('Error'),
                            _("Formula must contain 'result' variable"))
                    res[product.id] = amount
        else:
            res = super(ProductProduct, self).price_get(
                cr, uid, ids, ptype=ptype, context=context)
        return res
