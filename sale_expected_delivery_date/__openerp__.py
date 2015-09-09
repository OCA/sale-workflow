# -*- coding: utf-8 -*-
#
#
#    Author: Kitti U. <kittiu@gmail.com>
#    Copyright 2015 Ecosoft
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
    'name': 'Sales Expected Delivery Date',
    'version': '1.0',
    'author': "Ecosoft, Odoo Community Association (OCA)",
    'category': 'Sale',
    'license': 'AGPL-3',
    'website': "http://www.ecosoft.co.th",
    'depends': ['sale',
                'sale_stock'
                ],
    'data': ['view/sale_view.xml',
             ],
    'auto_install': False,
    'installable': True,
}
