# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Odoo.com.
#    Copyright (C) 2015 Openies.com.
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
    'name': 'Allotment on sale orders',
    'version': '8.0.1.1.0',
    'category': 'Sales',
    'summary': "Separate the shipment according to allotment partner",
    'author': u'Openies,Numérigraphe,Odoo Community Association (OCA)',
    'website': 'http://www.Openies.com/',
    'depends': ['sale_stock'],
    'data': [
        'views/sale_order_line_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
