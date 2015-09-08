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
    'version': '8.0.1.1.1',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'description': """
Product Pack
============
Withilist:
----------
* TODO calcular correctamente pack virtual available para negativos
* Add configuration to enable "group_pack" functionality, now you have to set
it manually
(seria para el group group_pack) y ver que se haga visible la vista form
* Improove packs interaction from product.template views
* Analize if better to unify sale_order_pack to pack_price_type selection
(perhups no because this functionality is only available if group "group_pack"
is active)
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
        'views/pack_view.xml',
        'views/sale_view.xml',
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
