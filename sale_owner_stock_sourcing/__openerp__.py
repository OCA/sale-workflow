# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher, Leonardo Pistone
#    Copyright 2014-2015 Camptocamp SA
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
{"name": "Sale Owner Stock Sourcing",
 "summary": "Manage stock ownership on sale order lines",
 "version": "8.0.0.1.0",
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "license": "AGPL-3",
 "category": "Purchase Management",
 'complexity': "normal",
 "images": [],
 "website": "http://www.camptocamp.com",
 "depends": ['sale_stock',
             'stock_ownership_availability_rules',
             ],
 "demo": [],
 "data": ['view/sale_order.xml',
          'security/group.xml',
          ],
 'installable': True,
 "auto_install": False,
 }
