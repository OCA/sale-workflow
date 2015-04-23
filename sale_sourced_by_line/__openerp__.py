# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2013-2014 Camptocamp SA
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

{'name': 'Sale Sourced by Line',
 'summary': 'Multiple warehouse source locations for Sale order',
 'version': '1.1',
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'expert',
 'images': [],
 'website': "http://www.camptocamp.com",
 'description': """
Sale Sourced by Line
====================

Adds the possibility to source a line of sale order from a specific
warehouse instead of using the warehouse of the sale order.

This will create one procurement group per warehouse set in sale
order lines.

It will only supports routes such as MTO and Drop Shipping.

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>

""",
 'depends': ['sale_stock',
             'sale_procurement_group_by_line',
             ],
 'demo': [],
 'data': ['view/sale_view.xml',
          ],
 'test': ['test/sale_order_source.yml',
          'test/sale_order_multi_source.yml',
          'test/sale_order_not_sourced.yml',
          ],
 'auto_install': False,
 'installable': True,
 }
