# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    'name': "Sale multi pickings",
    'version': '0.1',
    'category': 'Sales Management',
    'summary': "Multi Pickings from Sale Orders",
    'description': """
This module allows to generate several pickings from the same sale order.
You just have to indicate which order lines have to be grouped in the same
picking. When confirming the order, for each group a picking is generated.
""",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    "depends": ['sale_stock'],
    "data": [
        'sale_view.xml',
        'security/ir.model.access.csv',
    ],
    "demo": [
        'sale_demo.xml',
    ],
    "active": False,
    'installable': False
}
