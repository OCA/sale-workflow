# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    @author Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#    @author Alex Comba <alex.comba@agilebg.com>
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
    'name': "Product price properties based",
    'version': '0.1',
    'category': '',
    'description': """
This module allows to use python formaulas to compute the sale order line
price.

You can configure the 'Price formula' on the product form using python code.

Formula example:
```
area = float(properties['Width']) * float(properties['Length'])
result = area / 2.0
if 'Painting' in properties:
    result = result + 5
```

When changing properties on sale order line, the system will automatically
compute the line price unit.


Contributors
------------

 - Lorenzo Battistini <lorenzo.battistini@agilebg.com>
 - Alex Comba <alex.comba@agilebg.com>

""",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": [
        'sale_properties_easy_creation',
        'web_context_tunnel',
    ],
    "data": [
        'sale_order_view.xml',
        'product_view.xml',
    ],
    "demo": [
        'product_demo.xml',
    ],
    "test": [
        'test/sale_order.yml',
    ],
    "active": False,
    "installable": True
}
