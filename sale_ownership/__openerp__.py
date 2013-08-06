# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

{'name': 'Sale Ownership',
 'version': '0.1',
 'author': 'Camptocamp',
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'advanced',
 'images': [],
 'website': "http://www.camptocamp.com",
 'description': """
Sale Ownership
==============

If there is an ownership defined on the stock locations, considering that
each sale order line can have a different source location, the workflow
of a sale will behave as follows (for MTS lines):

1. If the sales order's customer is different than the stock location owner,
   a purchase order is generated for the line and linked with the picking.
2. If the sales order's customer is the same than the stock location owner,
   then the prices of the lines should be 0. This happens when a supplier
   stores its own material in warehouse, and he want to get it back. Some fees
   can still be added manually.
""",
 'depends': ['stock_location_ownership',
             'sale_sourced_by_line',
             'sale_dropshipping',
             ],
 'demo': [],
 'data': [],
 'test': [],
 'auto_install': False,
 'installable': True,
 }
