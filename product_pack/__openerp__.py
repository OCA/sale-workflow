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
    'version': '1.0',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'description': """
Product Pack
============
# TODO agregar en configuracion si se quiere usar los sale order packs (seria para el group group_pack) y ver que se haga visible la vista form
# TODO implementar totalice en price get
# TODO agregar constraint de no pack dentro de pack
# TODO calcular correctamente pack virtual available para negativos
    """,
    'author':  'NaN·tic, ADHOC',
    'images': [
    ],
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/product_security.xml',
        'pack_view.xml',
        'sale_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
