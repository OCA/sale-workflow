# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Opener B.V. (<https://opener.am>)
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
    'name': 'Default sales incoterm per partner',
    'version': '8.0.1.0.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': "Set the customer preferred incoterm on each sales order",
    'author': "Opener B.V.,Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/sale-workflow',
    'depends': ['sale_stock'],
    'data': [
        'views/res_partner.xml',
    ],
    'installable': True,
}
