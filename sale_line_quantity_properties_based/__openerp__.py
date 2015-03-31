# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Authors: Alex Comba <alex.comba@agilebg.com>
#             Lorenzo Battistini <lorenzo.battistini@agilebg.com>
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
    'name': "Sale line quantity properties based",
    'version': '0.1',
    'category': 'Sales Management',
    'description': """
Sale line quantity based on line properties
===========================================

*This module allows the calculation of the product quantity on the basis of a
formula that considers the properties specified by the user on the sale order
line and on the quantity (UoS).*

Example
--------

Provided the sale of a given number of pieces (shelves), that may be
’x’ meter long and ’y’ meter large, the formula enables the calculation of the
total area sold expressed in square meters:
    10 [pcs of] (4 m x 0.5 m) shelves = 20 m² of wood

In order to have this function working, it is necessary to have the user
proceeding as follows:

Then s/he shall create properties such as ‘length 4’, ‘width 0.5’.
(Note: this can be more easily achieved by using the modules
'sale_properties_easy_creation' and/or 'sale_properties_dynamic_fields')

Properties must respond the following criteria:
    * Name: ‘length 1’, ‘length 4’, ‘width 0.5’
    * Property Group : either ‘length’ or ‘width’
    * Value : the corresponding quantity (1, 4, 0.5...)

Property 'length 4'
    * Name: ‘length 4’
    * Property Group : ‘length’
    * Value : 4

Property 'width 0.5'
    * Name: ‘width 0.5’
    * Property Group : ‘width’
    * Value : 0.5

After this, the formula 'surface' must be created and associated
to the product:

```
result = float(properties['length']) * float(properties['width']) * qty_uos
```

Upon the registering of the order, the user will apply in the properties field
the desired properties (in this example the ‘lenght 4’ and ‘width 2’), the
needed formula (in this example 'surface') and last the quantity (UoS).


Contributors
------------

* Alex Comba <alex.comba@agilebg.com>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
""",
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    'depends': [
        'sale_mrp',
        'sale_properties_easy_creation',
        'web_context_tunnel',
    ],
    'data': [
        'sale_order_view.xml',
        'product_view.xml',
    ],
    'test': [
        'test/sale_line_quantity_properties_based.yml',
    ],
    'installable': True
}
