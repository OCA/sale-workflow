# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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
    "name": "Product Special Types",
    "version": "1.0",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Sales",
    "description":
    """
Add a special type selection on products.
Let create products as :
 - Global Discount
 - Delivery Costs
 - Advance

It add fields on the sale order and the invoice with the totals of each
product types.
These fields can be used on reports to display the amounts for
discounts / advances / fees separately.

""",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ['base',
                'product', ],
    "init_xml": [],
    "demo_xml": [],
    "update_xml": ['product_view.xml'],
    "active": False,
    'installable': False
}
