# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume
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

{'name': 'Sale No stock by line',
 'version': '0.1',
 'author': 'Camptocamp',
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'expert',
 'images': [],
 'website': "http://www.camptocamp.com",
 'description': """
Sale No stock by line
=====================

This module depends on both sale_exception_nostock and sale_sourced_by_line and make the 
exception occure based on the location of each line.

The principle of the no-stock exception is to raise a warning when no enough stock are
gound in the location of the SO shop. This module make the warning occure for every line
location instead of looking at the shop location for all line.

""",
 'depends': [
    'sale_exception_nostock',
    'sale_sourced_by_line',
             ],
 'demo': [],
 'data': [],
 'test': [],
 'auto_install': False,
 'installable': True,
 }
