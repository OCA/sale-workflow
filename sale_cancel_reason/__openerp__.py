# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
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

{'name': 'Sale Cancel Reason',
 'version': '8.0.1.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'category': 'Sale',
 'license': 'AGPL-3',
 'complexity': 'normal',
 'images': [],
 'website': "http://www.camptocamp.com",
 'description': """
Sale Cancel Reason
==================

When a sale order is canceled, a reason must be given,
it is chosen from a configured list.

""",
 'depends': ['sale',
             ],
 'demo': [],
 'data': ['wizard/cancel_reason_view.xml',
          'view/sale_view.xml',
          'security/ir.model.access.csv',
          'data/sale_order_cancel_reason.xml',
          ],
 'auto_install': False,
 'test': ['test/sale_order_cancel.yml',
          ],
 'installable': True,
 }
