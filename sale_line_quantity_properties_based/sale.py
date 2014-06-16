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
import traceback


class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'

    def onchange_formula(
            self, cr, uid, ids,
            formula_id, property_ids, product_uos_qty, context=None
    ):
        res = {}
        properties = {}
        warning_msg = ''
        warning = {'title': _('Formula Error!')}
        if formula_id and property_ids:
            formula = self.pool.get('sale.order.line.quantity.formula').browse(
                cr, uid, formula_id, context=context)
            formula_text = formula.formula_text
            mrp_property_obj = self.pool.get('mrp.property')
            for mrp_property_id in property_ids[0][2]:
                mrp_property = mrp_property_obj.browse(
                    cr, uid, mrp_property_id, context=context)
                if not mrp_property.description:
                    warning_msg = _(
                        u"The property %s has the field description "
                        u"not filled" % mrp_property.name
                    )
                    break
                if mrp_property.group_id.name in properties:
                    warning_msg = _(
                        u"The formula %s cannot work since "
                        u"there are more than one property belong "
                        u"to the same group" % formula_text
                    )
                    break
                try:
                    properties[mrp_property.group_id.name] = float(
                        mrp_property.description)
                except ValueError:
                    warning_msg = _(
                        u"%s is not a valid value for the "
                        u"property %s, it must be a number"
                        % (
                            mrp_property.description,
                            mrp_property.group_id.name
                        )
                    )
                    break
            if warning_msg:
                warning.update({'message': warning_msg})
                return {'warning': warning}
            try:
                res['product_uom_qty'] = eval(formula_text.replace(
                    'P', 'properties')) * product_uos_qty
            except Exception, e:
                formatted_lines = traceback.format_exc().splitlines()
                warning_msg = _(
                    u"%s is not a valid formula. Reason: %s"
                    % (
                        formula_text,
                        formatted_lines[-1]
                    )
                )
                warning.update({'message': warning_msg})
                return {'warning': warning}
        return {'value': res}

    _columns = {
        'formula_id': fields.many2one(
            'sale.order.line.quantity.formula', 'Formula',),
    }


    def product_id_change(
            self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None
    ):
        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name,
            partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag, context=context
        )
        if 'value' in res and 'product_uos_qty' in res['value']:
            del res['value']['product_uos_qty']
        return res


class sale_order_line_quantity_formula(orm.Model):
    _name = "sale.order.line.quantity.formula"

    _columns = {
        'name': fields.char('Name', size=32),
        'formula_text': fields.text('Formula'),
    }
