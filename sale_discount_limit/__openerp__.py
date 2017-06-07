# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Sistemas Adhoc
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
    'name': 'Sale Discount Limit',
    'summary': "Set a maximum allowed discount for sales quotations",
    'version': '1.0',
    'author': 'Eficent, Odoo Community Association (OCA)',
    'website': 'http://www.eficent.com',
    "license": "AGPL-3",
    'depends': ['sale'],
    'init_xml': [],
    'update_xml': [
        'security/sale_discount_limit_security.xml',
        'security/ir.model.access.csv',
        'view/sale_workflow.xml',
        'view/sale_view.xml',
        'view/product_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}