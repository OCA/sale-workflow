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


class ProductProduct(orm.Model):
    _inherit = "product.product"

    _columns = {
        'quantity_formula_id': fields.many2one(
            'mrp.property.formula', 'Quantity formula',
            help="You can use the variables\n"
                 " - self\n"
                 " - cr\n"
                 " - uid\n"
                 " - product_id\n"
                 " - properties (dictionary of properties)\n"
                 "You have to put the result in the 'result' variable"),
    }
