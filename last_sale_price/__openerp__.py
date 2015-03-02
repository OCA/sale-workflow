# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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
{'name': 'Last Sale Price',
 'summary': 'Show last price defined for customer on sale order line',
 'version': '1.0',
 'category': 'Sales',
 'description': """
Last Sale Price
===============

Add price, quantity and date of a product of the last time it was sold to
a partner.

In order to let the salesman know if a customer already ordered a product.
And to give him hint about what price he should propose.
That information is shown next to the price in Sale Order's line Form.

Only Sale Orders' lines in state Confirmed and Done are considered to
compute those fields.

If multiple Sale Order lines for the same partner where made on the same
date for the same product, the sum of all quantity and the average price
will be displayed.
""",
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['base', 'sale'],
 'data': ['sale_view.xml'],
 'test': ['test/last_sale_price.yml'],
 'installable': True,
 'auto_install': False,
 'application': False,
 }
