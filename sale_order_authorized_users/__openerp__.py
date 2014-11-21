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
===========================
This module allows you to implement "secret" sale orders.
Users in the 'Sale / Secret orders' group will see a new field on sale orders,
"Allowed Users", that can be used to restrict access to that sale order to
selected users.

Details
-------
This acts as an **additional restriction**, access rules are still considered:
for example, an user in the "Own leads only" group won't be able to see
an order that it's not his, even if he's selected as allowed.

On the other hand, by setting some users as allowed, all other
users, even if they are "See all leads", won't be able to see the order.

*When you add allowed users to a sale order, unless you're connected as admin,
you must include yourself, or you won't be able make the change!*

If no users are set (the default), all users are considered as allowed,
so the sale order follows the "normal" access rules with no additional
restrictions.
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
