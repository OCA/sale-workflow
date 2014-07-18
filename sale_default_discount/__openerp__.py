# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
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
    'name': 'Sale Default Discount',
    'version': '1.0',
    'category': 'Generic Modules/Sale',
    'description': """
Sale Default Discount
=====================

This module allows to set a default discount per customer and per sale order.

The customer discount is used by default when creating an order, and the
order default is used when creating new order lines.

The defaults can be left empty, keeping the default behaviour.

Contributors
------------

  * Leonardo Pistone <leonardo.pistone@camptocamp.com>

""",
    'author': 'Camptocamp',
    'depends': ['sale'],
    'website': 'http://www.camptocamp.com',
    'data': [
        'view/partner.xml',
        'view/sale.xml',
    ],
    'test': [
        'test/no_default_discount.yml',
        'test/partner_default_discount.yml',
    ],
    'demo': [],
    'installable': True,
    'active': False,
}
