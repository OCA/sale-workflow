# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2015 JPJ
#    ( http://www.savoirfairelinux.com).
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
    'name': 'Sale Reason to Export',
    'version': '8.0.0.1.0',
    'author': 'Jean-Philippe Jobin',
    'maintainer': 'Savoir-faire Linux',
    'website': 'https://github.com/OCA/sale-workflow',
    'license': 'AGPL-3',
    'category': 'Sales',
    'summary': 'Reason to export in Sales Order',
    'depends': [
        'sale',
    ],
    'external_dependencies': {
        'python': [],
    },

    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/sale_reason_to_export_view.xml',
    ],

    'installable': False,
    'auto_install': False,
    'application': False,
}
