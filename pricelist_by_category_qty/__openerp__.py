# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

{
    "name" : "Discount by quantities of product category",
    "version" : "0.1",
    "author" : "Julius Network Solutions",
    "website" : "http://julius.fr",
    "category" : "Sales Management",
    "depends" : [
        'sale',
    ],
    "description": """
    This module will add a button inside the sale order and will compute the discount
    not by line but by quantities of the same product category, in the same sale order.
    e.g.:
    You've defined 10% discount for Category A for 100 PCE min in the List price.
    You try to sell 50 Pieces of Product A and 50 Pieces of Product B (defined on Category A).
    The OnChange in the line will compute the price of the product as usual.
    Then you click on the new button. The unit price will be updated as you've sold 50+50 = 100 pieces of the same category!
    => you will have 10% discount on both lines !
    """,
    "demo" : [],
    "data" : [
        'sale_view.xml',
    ],
    'installable' : False,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
