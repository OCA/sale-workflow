# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-guillaume (Camptocamp)
#    Copyright 2011 Camptocamp SA
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
    'name' : 'Sales Order with Department Categorization',
    'version' : '1.0',
    'category' : 'Generic Modules/Sales & Purchases',
    'description':
'''
    Add the department on Sales Order and Customer Invoices as well as the related filter and button in the search form.

''',
    'author' : 'Camptocamp',
    'website': 'http://camptocamp.com',
    'depends' : ['sale', 'invoice_department', 'hr'],
    'data' : [
        'sale_view.xml',
    ],
    'demo' : [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
