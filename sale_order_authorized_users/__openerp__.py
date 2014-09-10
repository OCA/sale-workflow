# -*- coding: utf-8 -*-
##############################################################################
#
# Author: Leonardo Donelli @ Creativi Quadrati
# Copyright (C) 2014 Leonardo Donelli
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Sale Order Authorized Users',
    'version': '1.0',
    'category': 'Sale',
    'summary': 'Sale orders, Security, Permissions, Users',
    'description': """
Sale Order Authorized Users
======================================

Let Admin (or any user in the base.group_erp_manager) choose,
for each sale order, which users will be able to access and see it.
Any other user won't be able to see it.
If no users are set, the sale order has normal permissions.
The field to set allowed users will be visibile only to admin, which makes it
possible to make the users unaware of this feature.
""",
    'author': 'Creativi Quadrati',
    'website': 'http://www.creativiquadrati.it',
    'depends': ['sale'],
    'data': [
        'sale_view.xml',
        'security/hide_sale_orders_security.xml',
    ],
    'test': [
        'test/sale_order.yml',
    ],
    'installable': True,
    'auto_install': False,
}
