# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#   @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'Sale Credit Note',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """This module introduce the concept of credit note on sales.
    You can pay a part of a sale order with available credit note
    created from refunds.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['sale_payment_method'],
    'data': [
        'wizard/new_credit_note_view.xml',
        'sale_view.xml',
        'invoice_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
}
