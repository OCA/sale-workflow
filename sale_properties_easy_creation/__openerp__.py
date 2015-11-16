# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl
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
    'version': '8.0.1.0.0',
    'category': 'Sales Management',
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": [
        'sale_mrp',
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
    "installable": True
}
