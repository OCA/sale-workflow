# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
    'name': 'Sale Order Amount to Invoice',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': 'Show amount left to invoice in sale order tree',
    'description': """
Sale Order Amount to Invoice
============================

This module adds a field "amount_to_invoice" on sale orders and displays
it in the tree view. The field is calculated as
   to invoice = (total - sum(total_amount for each invoice_id))

Contributors
------------
* Vincent Vinet (vincent.vinet@savoirfairelinux.com)
* Marc Cassuto (marc.cassuto@savoirfairelinux.com)
""",
    'depends': [
        'sale',
        'account',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'sale_order_view.xml',
        'account_invoice_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
