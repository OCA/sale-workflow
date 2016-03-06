# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#    @author Lorenzo Battistini <lorenzo.battistini@agilebg.com>
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
##############################################################################

{
    'name': "Sale order revisions",
    'version': '8.0.0.1.0',
    'category': 'Sale Management',
    'author': 'Agile Business Group,'
              'Camptocamp,'
              'Akretion,'
              'Odoo Community Association (OCA)',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": ['sale'],
    "data": [
        'view/sale_order.xml',
        ],
    "test": [
        'test/sale_order.yml',
        ],
    "active": False,
    "installable": True,
    "post_init_hook": 'populate_unrevisioned_name',
}
