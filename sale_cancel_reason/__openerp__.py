# -*- coding: utf-8 -*-
#
#
#    Author: Guewen Baconnier
#    Copyright 2013 Camptocamp SA
#    Copyright 2016 Serpent Consulting Services Pvt. Ltd.
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
#

{
    'name': 'Sale Cancel Reason',
    'version': '9.0.1.0.0',
    'author': 'Camptocamp, Odoo Community Association (OCA), '
              'Serpent Consulting Services Pvt. Ltd.',
    'category': 'Sale',
    'license': 'AGPL-3',
    'website': "http://www.camptocamp.com",
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sale_order_cancel_reason.xml',
        'wizard/cancel_reason_view.xml',
        'views/sale_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
