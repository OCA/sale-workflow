# -*- coding: utf-8 -*-
#
#
#    Author: Alexandre Fayolle
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
#
{
    'name': 'Purchase order lines with sequence number',
    'version': '0.1',
    'category': 'Purchase Management',
    'description': '''
Provide a new field on the purchase order form, allowing to manage the lines
order.
    ''',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'website': 'http://www.camptocamp.com',
    'depends': [
        'purchase',
        'stock_picking_reorder_lines',
        'account_invoice_reorder_lines'
    ],
    'data': ['purchase_view.xml'],
    'demo': [],
    'test': [],
    'installable': False,
    'auto_install': False,
    'application': False,
    'license': "AGPL-3",
}
