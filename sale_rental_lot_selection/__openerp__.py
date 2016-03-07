# -*- coding: utf-8 -*-
##############################################################################
#
#    Sale Rental Lot Selection module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
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
    'name': 'Sale Rental Lot Selection',
    'version': '8.0.1.0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Manage Rental with Serial Numbers',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['sale_order_lot_selection', 'sale_rental'],
    'data': ['rental_view.xml'],
    'installable': True,
    'auto_install': True,
}
