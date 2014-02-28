# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Camptocamp (<http://www.camptocamp.com>)
#    Authors: Joel Grand-Guillaume
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
    'name': 'Sale Service Just In Time',
    'version': '1.0',
    'category': 'Generic Modules/Sale',
    'description': """
Sale Service Just In Time
=========================

When you make a SO with product and services, the workflow of the SO will not reach
the state done unless you deliver all the products and the procurements linked to
services product are done.

Usualy, the when the mrp run, it mark the procurement of services line as done. But,
you  may want to mark them as done like if you were using the mrp_jit module.

This module provide that feature: It bring the behavior of the mrp_jit module
but only on services products.

 Contributors:
 -------------

  * Joël Grand-Guillaume <joel.grand-guillaume@camptocamp.com>

""",
    'author': 'Camptocamp',
    'depends': ['sale_stock'],
    'website': 'http://www.camptocamp.com',
    'data': [],
    'test': [
        'test/sale_service_jit_test.yml',
    ],
    'demo': [],
    'installable': True,
    'active': False,
}
