# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 AKRETION
#    @author Chafique Delli <chafique.delli@akretion.com>
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
    'name': 'Sale Team Invoice Partner',
    'version': '0.1',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': "Adds invoice partner in sales team for use in a sale order",
    'description': """
    This module adds a new field on the sales team form:
*Final Partner for Invoicing*. The value of this field will be used when you
create a new Sale Order with this sales team.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'sales_team',
        'sale'
    ],
    'data': [
        'sales_team_view.xml',
        'sale_view.xml',
    ],
    'installable': True,
}
