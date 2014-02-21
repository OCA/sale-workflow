# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Romain Deheele
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
##############################################################################

{
    "name": "Product Procurement Types",
    "version": "1.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Sales",
    "description":
    """
    Add a procurement type selection on products.
    Let create products as :
     - Standard
     - Bill of Materials

    Choose "Standard" changes automatically
    procurement method as "make to stock" and supply method as "buy".
    Choose "Bill of Materials" changes automatically
    procurement method as "make to order" and supply method as "produce".

    """,
    "website": "http://camptocamp.com",
    "depends": ['sale',
                'procurement',
                'mrp'],
    "data": ['product_view.xml'],
    "demo": [],
    "test": ['test/test_onchange_procurement_type.yml'],
    "active": False,
    "installable": True,
}
