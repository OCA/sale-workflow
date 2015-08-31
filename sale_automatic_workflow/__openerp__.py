# -*- encoding: utf-8 -*-
##############################################################################
#
#   sale_automatic_workflow for OpenERP
#   Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
#   Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
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
    'name': 'Sale Automatic Workflow',
    'version': '0.2',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'author': "Akretion,Camptocamp,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['sale_stock', 'sales_team',
                ],
    'data': ['sale_view.xml',
             'sale_workflow.xml',
             'sale_workflow_process_view.xml',
             'automatic_workflow_data.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
}
