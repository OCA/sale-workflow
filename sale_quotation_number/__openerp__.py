# -*- coding: utf-8 -*-
#
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
#


{
    'name': 'Sale Quotation Numeration',
    'version': '8.0.1.1.0',
    'category': 'Sales Management',
    'summary': "Different sequence for sale quotations",
    'description': """
This module adds a sale quotation sequence.
===========================================

Defining.

*Sale Quotation:* Sale process in draft stage just informing prices and element
of communication.
*Sale Order:* Sale process confirmed, the customer already have a compromise
with us in terms of pay an invoice and receive our product or service.

Originally OpenERP manage only 1 sequence for this 2 documents, then the sales
order won and lost manage the same sequence losting almost all lost quotations
in terms of sequences, making so difficult understand qith a quick view if we
are good or bad in terms of logistic and sale process already confirmed.

Technical Explanation:

When you create a quotation, it is numbered using the 'sale.quotation'
sequence.  When you confirm a quotation, its orginal number is saved in the
'origin' field and the sale order gets a new number, retrieving it from
'sale.order' sequence.

With Openerp Base.

Sale Quotation 1 Number = SO001
Sale Quotation 2 Number = SO002
Sale Quotation 3 Number = SO003
Sale Quotation 4 Number = SO004

Sale Quotation 2 Confirmed = Number for Sale Order SO004

With Openerp + This Module.


Sale Quotation 1 Number = SQ001
Sale Quotation 2 Number = SQ002
Sale Quotation 3 Number = SQ003
Sale Quotation 4 Number = SQ004

Sale Quotation 2 Confirmed = Number for Sale Order SO001 from Sale Quotation
SQ002

Sale Quotation 1 Confirmed = Number for Sale Order SO002 from Sale Quotation
SQ001

Sale Quotation 4 Confirmed = Number for Sale Order SO003 from Sale Quotation
SQ004
""",
    'author': 'Elico Corp,'
              'Agile Business Group,'
              'Odoo Community Association (OCA)',
    'website': 'http://www.openerp.net.cn',
    'depends': ['sale'],
    'data': [
        'data/data.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
