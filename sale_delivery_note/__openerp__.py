# -*- coding: utf-8 -*-

##############################################################################
#
# Delivery Notes
# Copyright (C) 2014 OpusVL (<http://opusvl.com/>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Delivery Notes',
    'version': '0.1',
    'author': 'OpusVL, Odoo Community Association (OCA)',
    'website': 'http://opusvl.com/',
    'summary': 'Allow printing of delivery note',

    'category': 'Warehouse',

    'description': """Allow printing of delivery note from delivery order screen.
""",
    'images': [
    ],
    'depends': [
        'sale',
        'stock',
        'purchase',
        'base',
    ],
    'data': [
        'reports/delivery_note.xml',
        'views/stock_picking_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
