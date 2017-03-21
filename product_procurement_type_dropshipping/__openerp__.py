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
    "name": "Product Procurement Type Dropshipping",
    "version": "0.1",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Sales",
    "description":
    """
    Add a choice named 'dropshipping' in procurement_type selection
    introduced by product_procurement_type addon.
    Choose "Dropshipping" changes automatically
    procurement method as "make to order" and supply method as "buy".
    It checks if at least one supplier is associated on supplier list
    in product form.

    """,
    "website": "http://camptocamp.com",
    "depends": ['product_procurement_type',
                'sale_dropshipping'],
    "data": ['product_view.xml'],
    "demo": [],
    "test": ['test/test_onchange_procurement_type.yml'],
    "active": False,
    "installable": True,
}
