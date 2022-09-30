# -*- coding: utf-8 -*-
#
#
#    Sale Fiscal Position Update module for OpenERP
#    Copyright (C) 2011-2014 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
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
    'name': 'Sale Fiscal Position Update',
    'version': '1.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Changing the fiscal position of a sale order will auto-update '
               'sale order lines',
    'description': """
Sale Fiscal Position Update
===========================

With this module, when a user changes the fiscal position of a sale order, the
taxes on all the sale order lines which have a product are automatically
updated. The sale order lines without a product are not updated and a warning
is displayed to the user in this case.

Contributors :

* Mathieu Vatel <mathieu _at_ julius.fr>

* Alexis de Lattre <alexis.delattre@akretion.com>
""",
    'author': "Julius Network Solutions, Akretion,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/sale-workflow',
    'depends': ['sale'],
    'data': ['sale_view.xml'],
    'installable': False,
    'active': False,
}
