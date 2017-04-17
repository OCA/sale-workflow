# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Chafique Delli
#    Copyright 2015 Akretion SA
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
    'name': 'Sale Mrp Sub State',
    'version': '0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'description': """
    This module allows to complete the sub state of the sale order
    with the different stages of production.
    """,
    'author': 'Akretion',
    'website': 'http://wwww.akretion.com/',
    'depends': ['mrp',
                'base_sale_sub_state',
                ],
    'data': [],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
