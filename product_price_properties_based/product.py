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


class ProductProduct(orm.Model):
    _inherit = "product.product"

    _columns = {
        'price_formula_id': fields.many2one(
            'mrp.property.formula', 'Price formula'),
        }

    def price_get(self, cr, uid, ids, ptype='list_price', context=None):
        if 'properties' in context:
            res = {}
            for product in self.browse(cr, SUPERUSER_ID, ids, context=context):
                localdict = {
                    'self': self,
                    'cr': cr,
                    'uid': uid,
                    'ptype': ptype,
                    'properties': context['properties'],
                }
                exec product.price_formula_id.formula_text in localdict
                amount = localdict['result']
                res[product.id] = amount
            return res
        else:
            res = super(ProductProduct,self).price_get(
                cr, uid, ids, ptype=ptype, context=context)
        return res
