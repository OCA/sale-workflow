# -*- coding: utf-8 -*-
##############################################################################
#
#   sale_payment_method for OpenERP
#   Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
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
##############################################################################


{
    'name': 'Sale Quick Payment',
    'version': '8.0.3.0.0',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['sale_payment_method',
                'sale_exceptions',
                ],
    'data': ['wizard/pay_sale_order.xml',
             'sale_view.xml',
             'settings/sale.exception.csv',
             ],
    'installable': True,
}
