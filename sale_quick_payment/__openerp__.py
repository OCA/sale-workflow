# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   sale_quick_payment for OpenERP                                            #
#   Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################


{
    'name': 'sale_quick_payment',
    'version': '6.1.0',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """
    Sale Quick Payment give the posibility to paid an sale order.
    The payment will be linked to the sale order
    If you install the module Sale Automatic Workflow you can forbid the validation
    of an unpaid order and also the Invoice will be automatically reconciled with
    the payment.
    This module was design for e-commerce sector.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'sale',
        'account_voucher',
        ], 
    'init_xml': [],
    'update_xml': [ 
            'sale_view.xml',
            'payment_method_view.xml',
            'wizard/pay_sale_order.xml',
            'company_view.xml',
            'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

