# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alex Comba <alex.comba@agilebg.com>
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


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def onchange_formula(
            self, cr, uid, ids, formula_id, property_ids, context=None
    ):
        res = {}
        formula = self.pool.get('sale.order.line.quantity.formula').browse(
            cr, uid, formula_id, context=context)
        formula_text = formula.formula_text
        res['product_uom_qty'] = 0
        return {'value': res}

    _columns = {
        'formula_id': fields.many2one(
            'sale.order.line.quantity.formula', 'Formula',),
    }


class sale_order_line_quantity_formula(orm.Model):
    _name = "sale.order.line.quantity.formula"

    _columns = {
        'name': fields.char('Name', size=32),
        'formula_text': fields.text('Formula'),
    }
