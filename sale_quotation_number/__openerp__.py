# -*- coding: utf-8 -*-
##############################################################################
#  
#    Copyright (c) 2010-2012 Elico Corp. All Rights Reserved.
#    Author:            Andy Lu <andy.lu@elico-corp.com>
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    Author:            Lorenzo Battistini <lorenzo.battistini@agilebg.com>
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
    'name': 'Sale Quotation Numeration',
    'version': '1.1',
    'category': 'Sales Management',
    'description': """
This module adds a sale quotation sequence.
When you create e quotation, it is numbered using the 'sale.quotation' sequence.
When you confirm a quotation, its orginal number is saved in the 'origin' field and the sale order gets a new number, retrieving it from 'sale.order' sequence.
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
