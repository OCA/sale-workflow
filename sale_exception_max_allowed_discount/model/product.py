# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class Product(orm.Model):
    _inherit = "product.product"

    _columns = {
        'has_max_sale_discount': fields.boolean('Applicable Maximum Discount'),
        'max_sale_discount': fields.float(
            'Maximum Discount (%)',
            digits_compute=dp.get_precision('Discount'),
            help="Maximum sales discount defined for this product. Sales "
                 "quotations containing products where the discount of the "
                 "line exceeds the discount defined in the product will be "
                 "blocked."),
    }

    _sql_constraints = [
        ('max_sale_discount_max_limit', 'CHECK (max_sale_discount <= 100.0)',
         _('Maximum discount must be lower than 100%.')),
        ('max_sale_discount_min_limit', 'CHECK (max_sale_discount >= 0.0)',
         _('Maximum discount must be higher than 0%.')),
    ]

    _defaults = {
        'has_max_sale_discount': False,
        'max_sale_discount': 0.0,
    }

    def onchange_has_max_sale_discount(self, cr, uid, ids,
                                       has_max_sale_discount, result=None):
        if result is None:
            result = {'value': {}}
        if not has_max_sale_discount:
            result['value']['max_sale_discount'] = 0.0
        return result

    def onchange_max_sale_discount(self, cr, uid, ids, max_sale_discount,
                                   result=None):
        if result is None:
            result = {'value': {}}
        if max_sale_discount:
            result['value']['has_max_sale_discount'] = True
        return result
