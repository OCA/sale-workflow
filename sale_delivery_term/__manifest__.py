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
    'name': "Sale delivery terms",
    'version': '0.1',
    'category': 'Sales Management',
    'summary': "Delivery term for sale orders",
    'description': """
Delivery term for sale orders.
You can configure delivery terms specifying the quantity percentage and the
delay for every term line.
You can then associate the term to the 'main' order line and generate
the 'detailed' order lines which in turn will generate several pickings
according to delivery term (thanks to 'sale_multi_picking' module).
""",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    "depends": ['sale_multi_picking'],
    "data": [
        'sale_view.xml',
        'security/ir.model.access.csv',
        'sale_data.xml',
    ],
    'test': [
        'test/sale_order_demo.yml',
    ],
    "demo": ['sale_demo.xml'],
    "active": False,
    'installable': False
}
