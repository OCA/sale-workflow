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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product visible discount extension',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': 'Product visible discount extension',
    'description': """
Product visible discount extension
==================================

This module is based on product_visible_discount that calculate
the discount rate on unit price calculated from a price list in
sale order lines. The discount rate can be either calculated from
the Public Price of the product and the unit price written in
the sale order line or set by the user.

Contributors
------------
* Loïc Faure-Lacroix (loic.lacroix@savoirfairelinux.com)
""",
    'depends': [
        'product_visible_discount',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'sale_view.xml',
    ],
    'installable': True,
}
