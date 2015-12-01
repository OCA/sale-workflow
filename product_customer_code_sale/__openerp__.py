# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    Author: Nicola Malcontenti <nicola.malcontenti@agilebg.com>
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
#
{
    "name": "Product Customer code on sale",
    "version": "1.0",
    "author": "Agile Business Group,Odoo Community Association (OCA)",
    "website": "http://www.agilebg.com",
    "category": "Sales Management",
    "depends": [
        'base',
        'product',
        'sale',
        'product_customer_code'
    ],
    "description": """
    Based on product_customer_code,
    this module loads in every sale order line
    the customer code defined in the product,
    """,
    "demo": [],
    "data": [
        'sale_view.xml',
    ],
    'installable': False,
    'active': False,
}
