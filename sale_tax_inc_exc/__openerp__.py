# -*- encoding: utf-8 -*-
###############################################################################
#
#   sale_tax_inc_exc for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>. All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'sale_tax_inc_exc',
    'version': '0.0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
    This module give the posibility to sale product with a price
    base on a tax inc or a tax exc.
    This module is experiental and may not work in your case
    (works perfectly for French case). You need accounting skill
    to configure it correctly
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['sale'], 
    'data': [ 
        'sale_view.xml',
        'account_view.xml',
        'invoice_view.xml',
        'product_view.xml',
    ],
    'demo': [],
    'installable': True,
    'active': False,
}

