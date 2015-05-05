# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    @author Lorenzo Battistini <lorenzo.battistini@agilebg.com>
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
{
    'name': "Easing properties input in sale order line",
    'version': '0.1',
    'category': '',
    'description': """
This modules simplifies the input of properties in the sale order line and
other places.

For instance, in the many2many field 'property_ids', it allows the user to
digit 'width 0.5' and the system will automatically create a property of group
'width' with value '0.5'

It also adds the model 'mrp.property.formula', to be used by computations based
on properties.
Used by modules like 'sale_line_price_properties_based' and
'sale_line_quantity_properties_based'
""",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": [
        'sale_stock',
        'mrp',
    ],
    "data": [
        'security/ir.model.access.csv',
        'mrp_property_view.xml',
        'mrp_property_formula_view.xml',
    ],
    "demo": [
        'mrp_property_group_demo.xml',
        'mrp_property_demo.xml',
        'mrp_property_formula_demo.xml',
    ],
    "test": [
        'test/properties.yml',
    ],
    "active": False,
    "installable": True
}
