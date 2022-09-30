# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi, Yannick Vaucher, Leonardo Pistone
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
#
{'name': 'Sale stock exception',
 'version': '8.0.1.2.0',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'category': 'sale',
 'complexity': "normal",
 'depends': ['sale_exception', 'sale_stock'],
 'description': """
Sale stock exception
--------------------

This addon adds two new sales exceptions to be used by the `sale_exception`
addon:

* The first one ensures that an order line can be delivered on the delivery
  date if it is in MTS. Validation is done by using the order line location via
  related shop and using the line delay.

* The second one will create a sales exception if the current SO will break a
  sales order already placed in the future.

The second test will only look for stock moves that pass by the line location,
so if your stock have children or if you have configured automated stock
actions they must pass by the location related to the SO line, else they will
be ignored.

If the module sale_owner_stock_sourcing is installed, each sale order line can
specify a stock owner. In that case, the owner will be used when computing the
virtual stock availability. For this to work correctly,
https://github.com/odoo/odoo/issues/5814 needs to be fixed (fixes are proposed
both for odoo and OCB).

**Warning:**

The second test is a workaround to compensate the lack of
stock reservation process in OpenERP. This can be a performance killer
and should not be be used if you have hundreds of simultaneous open SO.
""",
 'website': 'https://github.com/OCA/sale-workflow',
 'data': ["data/data.xml"],
 'demo': [],
 'test': ['test/no_stock_test.yml'],
 'installable': False,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False,
 }
