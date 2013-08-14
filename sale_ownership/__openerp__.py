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
 'complexity': 'expert',
 'images': [],
 'website': "http://www.camptocamp.com",
 'description': """
Sale Ownership
==============

As of today, this addon does nothing more than installing its
dependencies. Its final goal is to handle the use case of having goods
owned by a supplier in our stock.

Let's say we are a restaurant. We ask 10'000 bottles of wine to a supplier.
We receive the 10'000 bottles and store them in a stock location, but we
will not pay them directly. Instead, when we need bottles, we will take
them from the stock location and create an invoice that we have to pay to
our supplier.

Technically, we have more than one way to accomplish this and that's why
this addon does not do it actually, however, thanks to its dependencies,
it gathers the necessary pieces:

stock_location_ownership
  Adds an ownership on the location, meaning that we are able to store
  the bottles in a location and specify that the location is owned by our
  supplier.

sale_sourced_by_line
  A different source location can be choosed on each sales order line.
  So for one sale order line of 10 bottles, we can say that they will be
  taken from the location owned by our supplier.

sale_dropshipping
  Allows to use dropshipping for the bottles, that is, they are directly
  delivered from our supplier, as in some sense they have a stock
  location in our stock.
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
