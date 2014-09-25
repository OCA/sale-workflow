# -*- coding: utf-8 -*-
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    'name': "Sale Quotation Sourcing",

    'summary': "manual sourcing of sale quotations",
    'description': """
    This module implements manual sourcing of sale order lines from purchase
    order lines.

    Instead of having a the confirmation of a SO generate procurements which in
    turn may generate PO, we invert the process: in order to generate a quote
    for a customer, it can be necessary to ask our suppliers from some
    quotes. Once the quote is accepted by the customer and the user confirms
    the SO, a wizard is presented which enables choosing the different PO to
    use to source the SO lines. """,

    'author': "Camptocamp",
    'website': "http://www.camptocamp.com",

    'category': 'Sales',
    'version': '0.1',

    'depends': ['sale_stock', 'purchase'],

    # always loaded
    'data': ['views/sale_order_sourcing.xml',
             'views/sale_order.xml',
             # 'security/ir.model.access.csv',
             'security/group.xml',
             ],
    'test': [
        'test/setup_user.yml',
        'test/setup_product.yml',
        'test/test_standard_mto_sourcing.yml',
        'test/test_manual_mto_sourcing.yml',
    ],
    'external_dependencies': {'python': ['nose']},
}
