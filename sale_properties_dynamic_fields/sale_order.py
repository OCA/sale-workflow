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
from lxml import etree
from openerp.tools.translate import _


class SaleOrder(orm.Model):
    _inherit = 'sale.order'

    def fields_view_get(
        self, cr, uid, view_id=None, view_type='form', context=None,
        toolbar=False, submenu=False
    ):
        res = super(SaleOrder, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if res['name'] == u'sale.order.form':
            property_group_pool = self.pool['mrp.property.group']
            group_to_draw_ids = property_group_pool.search(cr, uid, [
                ('draw_dynamically', '=', True),
            ], context=context)
            if group_to_draw_ids:
                for group in property_group_pool.browse(
                    cr, uid, group_to_draw_ids, context=context
                ):
                    if not group.field_id:
                        raise orm.except_orm(
                            _('Error'),
                            _(
                                'The group %s has draw_dynamically set but '
                                'there is no linked field '
                            ) % group.name
                        )
                    if (
                        group.field_id.name in res['fields']['order_line'][
                            'views']['form']['fields']
                    ):
                        raise orm.except_orm(
                            _('Error'),
                            _('Field %s already present') % group.name)
                    field_name = group.field_id.name
                    res['fields']['order_line']['views']['form'][
                        'fields'
                    ].update(
                        {
                            field_name: {
                                'string': group.name,
                                'type': 'char',
                                'size': 64,
                                'context': {}
                            }
                        }
                    )
                    eview = etree.fromstring(
                        res['fields']['order_line']['views']['form']['arch'])
                    group_field = etree.Element(
                        'field', name=field_name,
                        on_change="dynamic_property_changed(property_ids, %s, "
                                  "context)"
                        % (field_name),
                        context="{\'field_name\': \'%s\'}" % field_name
                    )
                    prop_m2m_field = eview.xpath(
                        "//field[@name='property_ids']")[0]
                    prop_m2m_field.addprevious(group_field)
                    res['fields']['order_line']['views']['form'][
                        'arch'
                    ] = etree.tostring(eview, pretty_print=True)
        return res
