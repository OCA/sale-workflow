# -*- coding: utf-8 -*-
#
#
#    Copyright (C) 2012 Ecosoft (<http://www.ecosoft.co.th>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
{
    'name': 'Sales - Isolated Quotation',
    'version': '10.0.0.1.0',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'category': 'Sales',
    'description': """
This module separate quotation and sales order by adding order_type
as 'quotation' or 'sale_order' in sale.order model.

Quotation will have only 2 state, Draft and Done. Sales Order work as normal.
    """,
    'website': 'http://ecosoft.co.th',
    'depends': ['sale', ],
    'images': [],
    'data': [
        'data/ir_sequence_data.xml',
        'views/sale_views.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
