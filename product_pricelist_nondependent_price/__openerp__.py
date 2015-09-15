# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Richard deMeester (Willow IT)
#    Copyright 2014-2015 Willow IT Pty Ltd
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

{   'name': 'Non-dependent Pricelist Pricing',
    'summary': 'Allow a price on a pricelist to be a fixed value',
    'version': '1.0.0',
    'author': "Willow IT,Odoo Community Association (OCA)",
    'maintainter': 'Willow IT',
    'category': 'Sales Management',
    'depends': ['product'],
    'description': """
Non-dependent Pricelist Pricing
===============================

Adds a price calculation option on pricelists for the price to be not
dependent on another price, but to be a fixed value that is not at all
calculated. This is particularly useful if pricing is imported from an
external source (such as a supplier provided pricelist or through a
calculation in a spreadsheet).

Contributors
------------

* Richard deMeester <richard@willowit.com.au>
""",
    'website': 'http://www.willowit.com.au',
    'data': ['views/pricelist_view.xml'],
    'tests': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
 }
