# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
{'name': 'Sale maximum discount exceeded exception',
 'version': '1.2',
 'author': "Eficent,Odoo Community Association (OCA)",
 'maintainer': 'Eficent',
 'category': 'sale',
 'license': 'AGPL-3',
 'complexity': "normal",
 'depends': ['sale_exceptions'],
 'website': 'http://www.eficent.com',
 'data': [
     "data/data.xml",
     "view/product_view.xml",
     ],
 'demo': [],
 'test': ['test/max_discount_exceeded.yml'],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False,
 }
