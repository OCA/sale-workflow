# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Tax Included Excluded module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Sale Tax Included Excluded',
    'version': '0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Manage products with both prices included and prices excluded',
    'description': """
This modules aims at solving the issue faced by companies who do both
B2B with prices displayed *taxes excluded* and B2C with prices displayed
*taxes included*. By default in Odoo, it is not possible to manage both
with a proper presentation of sale orders and invoices. With this module
and a proper configuration, it becomes possible.

This modules requires a patch on the *sale* module and on the
*product_visible_discount* module (if it is installed).
In the future, if the pull request https://github.com/odoo/odoo/pull/3717
is merged in Odoo v8, we will be able to adapt this module and we will
not have to patch the official addons anymore.

This module has been written by Alexis de Lattre from Akretion
<alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['sale'],
    'data': [
        'account_view.xml',
        'price_type_view.xml',
        'wizard/product_price_view.xml',
    ],
    'installable': True,
}
