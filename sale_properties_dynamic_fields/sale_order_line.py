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

from openerp.osv import orm
from openerp.tools.translate import _
from openerp import exceptions


class SaleOrderLine(orm.Model):
    _inherit = 'sale.order.line'

    def test_property_presence(self, prop, prop_dict):
        if prop.group_id.name in prop_dict:
            raise exceptions.Warning(
                _('Property of group %s already present')
                % prop.group_id.name)

    def build_prop_m2m_from_dict(self, cr, uid, prop_dict, context=None):
        res = [(6, 0, [])]
        for prop_tuple in prop_dict.values():
            if prop_tuple[0] not in res[0][2]:
                res[0][2].append(prop_tuple[0])
        return res

    def dynamic_property_changed(
        self, cr, uid, ids, property_ids, dynamic_property, context=None
    ):
        res = {}
        prop_dict = {}  # properties already present on line
        if dynamic_property and context.get('field_name'):
            prop_pool = self.pool['mrp.property']
            field_pool = self.pool['ir.model.fields']
            group_pool = self.pool['mrp.property.group']
            field_ids = field_pool.search(cr, uid, [
                ('name', '=', context['field_name']),
                ('model', '=', 'sale.order.line'),
            ], context=context)
            if property_ids:
                for m2m_tup in property_ids:
                    for prop in prop_pool.browse(
                        cr, uid, m2m_tup[2], context=context
                    ):
                        self.test_property_presence(prop, prop_dict)
                        prop_dict[prop.group_id.name] = (prop.id, prop.value)
            if len(field_ids) != 1:
                raise exceptions.Warning(
                    _('There must be 1 and only 1 %s')
                    % context['field_name'])
            group_ids = group_pool.search(cr, uid, [
                ('field_id', '=', field_ids[0]),
            ], context=context)
            if len(group_ids) != 1:
                raise exceptions.Warning(
                    _('There must be 1 and only 1 group for %s')
                    % context['field_name'])
            group = group_pool.browse(cr, uid, group_ids[0], context=context)
            if group.name in prop_dict:
                del prop_dict[group.name]
            prop_ids = prop_pool.search(cr, uid, [
                ('group_id', '=', group.id),
                ('value', '=', dynamic_property),
            ], context=context)
            if prop_ids:
                prop = prop_pool.browse(cr, uid, prop_ids[0], context=context)
                prop_dict[group.name] = (prop.id, prop.value)
            else:
                prop_id = prop_pool.create(cr, uid, {
                    'name': '%s %s' % (group.name, dynamic_property),
                    'value': dynamic_property,
                    'group_id': group.id,
                }, context=context)
                prop_dict[group.name] = (prop_id, dynamic_property)
            res = {
                'value':
                    {
                        'property_ids': self.build_prop_m2m_from_dict(
                            cr, uid, prop_dict, context=context)
                    }
            }
        return res
