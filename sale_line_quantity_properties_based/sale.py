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
from openerp.tools.translate import _


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def onchange_formula(
            self, cr, uid, ids, formula_id, property_ids, context=None
    ):
        res = {}
        properties = {}
        warning = {}
        warning_msgs = False
        if formula_id:
            formula = self.pool.get('sale.order.line.quantity.formula').browse(
                cr, uid, formula_id, context=context)
            formula_text = formula.formula_text
            if property_ids:
                mrp_property_obj = self.pool.get('mrp.property')
                for mrp_property_id in property_ids[0][2]:
                    mrp_property = mrp_property_obj.browse(
                        cr, uid, mrp_property_id, context=context)
                    if mrp_property.group_id.name in properties:
                        warning_msgs = _("This formula cannot work")
                    try:
                        properties[mrp_property.group_id.name] = float(
                            mrp_property.description)
                    except ValueError:
                        warning_msgs = _(
                            u"%s is not a valid value for the "
                            u"property %s, it must be a number") % (
                            mrp_property.description,
                            mrp_property.group_id.name)
            try:
                res['product_uom_qty'] = eval(formula_text.replace(
                    'P', 'properties'))
            except Exception, e:
                warning_msgs = _(u"%s is not a valid formula") % (
                    formula_text)
        if warning_msgs:
            warning = {
                'title': _('Formula Error!'),
                'message': warning_msgs
            }
        return {'value': res, 'warning': warning}

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
