# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
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
###############################################################################

{
    'name': 'Price List Restrict Product in Sales',
    'version': '0.1',
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': ('Restrict product selection in sales order '
                'according to price list'),
    'description': """
Price List Restrict Product in Sales
====================================
This module restricts product selection in sales orders to the ones possibly
allowed by the current price list.

Contributors
------------
* Marc Cassuto (marc.cassuto@savoirfairelinux.com)
* Vincent Vinet (vincent.vinet@savoirfairelinux.com)
""",
    'depends': [
        'sale',
        'product',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [],
    'installable': True,
}
