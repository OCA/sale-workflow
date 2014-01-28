# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Start End Dates module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
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
    'name': 'Sale Start End Dates',
    'version': '0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Adds start date and end date on sale order lines',
    'description': """
Sale Start End Dates
====================

This module adds start date and end dates on sale order lines. The value of these field is copied to the start date and end date of invoice lines. This module is designed to be used with other modules such as sale_rental.

Please contact Alexis de Lattre from Akretion <alexis.delattre@akretion.com> for any help or question about this module.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['account_cutoff_prepaid', 'sale'],
    'data': [
        'sale_view.xml',
    ],
    'installable': True,
    'active': False,
}
