# -*- coding: utf-8 -*-
##############################################################################
#  
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#    Author:            Andy Lu <andy.lu@elico-corp.com>
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Sale Order Approvement',
    'version': '1.1',
    'category': 'Sales Management',
    'description': """
        Add a sale quotation sequence, when confirm it, generate a new sale order sequence.
        quotation name as source document.
    """,
    'author': ['Elico Corp', 'Agile Business Group'],
    'website': 'http://www.openerp.net.cn',
    'depends': ['sale'],
    'data': [
        'sale_quotation_view.xml',
    ],
    'demo': [], 
    'test': [],
    'installable': True,
    'active': False,
}
