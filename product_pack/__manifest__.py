##############################################################################
#
#    Copyright (C) 2009  Àngel Àlvarez - NaN  (http://www.nan-tic.com)
#    All Rights Reserved.
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
    'name': 'Product Pack',
    'version': '11.0.1.3.3',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'author': 'NaN·tic, ADHOC SA',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_pack_line_views.xml',
        'views/product_product_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_line_pack_line_views.xml',
        'views/sale_order_line_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [
        'demo/product_product_demo.xml',
        'demo/product_pack_line_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
