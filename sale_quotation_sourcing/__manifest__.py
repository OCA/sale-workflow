# -*- coding: utf-8 -*-
#
#    Author: Alexandre Fayolle, Leonardo Pistone
#    Copyright 2014-2015 Camptocamp SA
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

    'author': "Camptocamp,Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/sale-workflow",

    'category': 'Sales',
    'version': '8.0.0.3.1',

    'depends': ['sale_stock',
                'purchase',
                'stock_dropshipping',
                'sale_exception',
                'sale_procurement_group_by_line'],
    'data': ['views/sale_order_sourcing.xml',
             'views/sale_order.xml',
             'security/group.xml',
             'data/exceptions.xml',
             ],
    'test': [
        'test/setup_user.yml',
        'test/setup_product.yml',
        'test/setup_dropshipping.xml',
        'test/test_standard_mto_sourcing.yml',
        'test/test_standard_dropshipping.yml',
        'test/test_manual_mto_sourcing.yml',
        'test/test_manual_sourcing_dropshipping.yml',
    ],
    'installable': False,
}
