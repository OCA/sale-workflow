# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011-2012 Camptocamp SA
# @author Guewen Baconnier
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
     "name" : "Product Special Types",
     "version" : "1.0",
     "author" : "Camptocamp",
     "category" : "Sales",
     "description":
"""
Add a special type selection on products.
Let create products as :
 - Global Discount
 - Delivery Costs
 - Advance

It add fields on the sale order and the invoice with the totals of each product types.
These fields can be used on reports to display the amounts for discounts / advances / fees separately.

""",
     "website": "http://camptocamp.com",
     "depends" : ['base',
                  'product',],
     "init_xml" : [],
     "demo_xml" : [],
     "update_xml" : ['product_view.xml'],
     "active": False,
     "installable": True
}
