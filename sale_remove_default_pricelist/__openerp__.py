# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Savoir-faire Linux
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Sale Remove Default Price List',
    'version': '1.0',
    'category': 'Sale',
    'summary': 'Sale Remove Default Price List',
    'description': '''
Sale Remove Default Price List
==============================

This module allow to fix the default price list configured for the partner.

From partner form view, click on Quotations and Sales, to create a quotation.
In quotation form view, selecting the partner doesn't change the price list
configured for the partner.

Contributors
------------

* El Hadji Dem (elhadji.dem@savoirfairelinux.com)
''',
    'author': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'depends': [
        'sale',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
