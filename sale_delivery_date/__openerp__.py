# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
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
    'name': "Sale Delivery Date",
    'version': '0.1',
    'category': 'Sales Management',
    'summary': 'Adds delivery date to sale order lines',
    'description': """
This module adds the field "delivery_date" to sale order lines, and fills the
existing mandatory field "delay" with the difference at order validation.
""",
    'author': 'Camptocamp',
    'website': 'http://www.camptocamp.com',
    'license': 'AGPL-3',
    "depends": ['sale',
                'sale_stock'],
    "data": [
        "sale_view.xml",
    ],
    "demo": [],
    'test': [],
    "active": False,
    "installable": True
}
