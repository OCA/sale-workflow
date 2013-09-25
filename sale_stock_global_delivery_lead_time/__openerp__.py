# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
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
{
    'name' : 'Sale global delivery lead time',
    'version' : '0.1',
    'category' : 'Sales Management',
    'description': '''
    Provides a way of setting a delivery lead time for all lines of a sale order
    ''',
    'author' : 'Camptocamp',
    'website' : 'http://www.camptocamp.com',
    'depends' : ['sale_stock'],
    'data' : ['sale_stock_view.xml'],
    'demo' : [],
    'test' : [],
    'installable': True,
    'auto_install' : False,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
