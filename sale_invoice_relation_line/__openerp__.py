# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Chafique Delli
#    Copyright 2014 Akretion SA
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
    'name': 'Sale Invoice Relation Line',
    'version': '1.0.0',
    'category': 'Generic Modules',
    'author': 'Akretion',
    'license': 'AGPL-3',
    'description': """
    This module allows a suitable display of invoice lines for bundle
    product with the notion parent product and child products(components)
""",
    'website': 'http://wwww.akretion.com/',
    'depends': ['sale_stock_relation_line',
                'account'],
    'data': [
        'account_invoice_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
