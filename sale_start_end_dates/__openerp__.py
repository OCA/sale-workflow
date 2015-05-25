# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale Start End Dates module for Odoo
#    Copyright (C) 2014-2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Sale Start End Dates',
    'version': '8.0.0.1.0',
    'category': 'Sales Management',
    'license': 'AGPL-3',
    'summary': 'Adds start date and end date on sale order lines',
    'author': 'Akretion,Odoo Community Association (OCA)',
    'website': 'http://www.akretion.com',
    'depends': ['account_cutoff_prepaid', 'sale', 'web_context_tunnel'],
    'data': ['sale_view.xml'],
    'demo': ['sale_demo.xml'],
    'installable': True,
}
