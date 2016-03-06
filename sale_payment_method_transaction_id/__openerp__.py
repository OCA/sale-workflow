# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
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

{'name': 'Sale Payment Method - Transaction ID Compatibility',
 'version': '1.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Hidden',
 'depends': ['sale_payment_method',
             # base_transaction_id is in
             # https://github.com/OCA/bank-statement-reconcile/tree/7.0
             'base_transaction_id',
             ],
 'description': """
Sale Payment Method - Transaction ID Compatibility
==================================================

Link module between the sale payment method module
and the module adding a transaction ID field (`base_transaction_id` in the
`lp:banking-addons/bank-statement-reconcile-7.0` branch).

When a payment is created from a sales order with a transaction ID, the
move lines are created with the transaction id.

 """,
 'website': 'http://www.camptocamp.com',
 'data': [],
 'tests': [],
 'installable': False,
 'auto_install': True,
 }
