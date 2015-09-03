# -*- encoding: utf-8 -*-
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
    'name': 'Base Sale Sub State',
    'version': '0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'description': """
    This module allows to have a sub state in the sale order
    for indicating the status of the production or shipping for example.
    """,
    'author': 'Akretion',
    'website': 'http://wwww.akretion.com/',
    'depends': ['sale'],
    'data': ['sale_view.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
