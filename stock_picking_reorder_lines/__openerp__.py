# -*- coding: utf-8 -*-
#
#
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
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
    'name': 'Stock picking lines with sequence number',
    'version': '0.1',
    'category': 'Warehouse Management',
    'summary': '''
Provide a new field on stock moves, allowing to manage the orders of moves
in a picking.
    ''',
    'author': "Camptocamp,Odoo Community Association (OCA)",
    'website': 'http://www.camptocamp.com',
    'depends': ['stock', 'sale', 'sale_stock'],
    'data': ['stock_view.xml'],
    'demo': [],
    'test': ['test/invoice_from_picking.yml'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': "AGPL-3",
}
