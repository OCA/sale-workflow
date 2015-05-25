# -*- encoding: utf-8 -*-
##############################################################################
#
#    Rental module for Odoo
#    Copyright (C) 2014-2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Rental',
    'version': '0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Manage Rental of Products',
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['sale_start_end_dates', 'stock'],
    'data': [
        'sale_view.xml',
        'stock_view.xml',
        'rental_view.xml',
        'rental_data.xml',
        'wizard/create_rental_product_view.xml',
        'product_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['rental_demo.xml'],
    'installable': True,
}
