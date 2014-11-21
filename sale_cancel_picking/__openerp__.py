# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Akretion (http://www.akretion.com).
#    @author Adrien CHAUSSENDE <adrien.chaussende@akretion.com>
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
    'name': 'Sale Cancel Picking',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """
        Allows direct Sale cancellation.
        Cancels related picking by the same time.
        Logs will be stocked in a field of the sale order.
    """,
    'author': 'Akretion',
    'website': 'http://akretion.com',
    'depends': ['sale_stock', 'sale'],
    'data': [
        'sale_view.xml',
        ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
