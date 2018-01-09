# -*- coding: utf-8 -*-
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
    'version': '9.0.1.3.0',
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
        'views/pack_view.xml',
        'views/sale_view.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
