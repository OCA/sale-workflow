# -*- coding: utf-8 -*-
#
#
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

{'name': 'Partner Prepayment',
 'summary': 'Option on partner to set prepayment policy',
 'version': '8.0.1.0.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'website': 'https://github.com/OCA/sale-workflow',
 'category': 'Sales',
 'license': 'AGPL-3',
 'complexity': 'easy',
 'images': [],
 'description': """
Partner Prepayment
==================

Add a checkbox 'Use prepayment' on customers.
When it is activated, the invoicing policy on Sales Orders
is set to 'Before Delivery'.

""",
 'depends': ['sale_stock',
             ],
 'demo': [],
 'data': ['view/partner_view.xml',
          ],
 'test': ['test/sale_order_prepaid.yml',
          ],
 'installable': False,
 'auto_install': False,
 }
