# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of sale_order_partial_advance,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     sale_order_partial_advance is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     sale_order_partial_advance is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with sale_order_partial_advance.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "sale_order_partial_advance",

    'summary': """
        Sale Order Partial Advance """,

    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",

    'category': 'Sales Management',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'sale',
    ],

    # always loaded
    'data': [
        'data/product_data.xml',
        'wizard/sale_line_invoice.xml',
    ],
}
