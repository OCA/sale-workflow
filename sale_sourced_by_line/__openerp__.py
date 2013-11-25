# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
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

{'name': 'Sale Sourced by Line',
 'version': '0.1',
 'author': 'Camptocamp',
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'expert',
 'images': [],
 'website': "http://www.camptocamp.com",
 'description': """
Sale Sourced by Line
====================

Adds the possibility to source a line of sale order from a specific
location instead of using the location of the warehouse of the selected
shop
""",
 'depends': ['sale_stock',
             ],
 'demo': [],
 'data': ['view/sale_view.xml',
          ],
 'test': ['test/sale_order_source.yml',
          'test/sale_order_not_sourced.yml',
          ],
 'auto_install': False,
 'installable': False,
 }
