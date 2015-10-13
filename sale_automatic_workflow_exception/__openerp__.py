# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2014 Akretion (http://www.akretion.com).
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
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
###############################################################################

{'name': 'Sale Automatic Workflow Exception',
 'version': '0.0.1',
 'author': "Akretion,Odoo Community Association (OCA)",
 'website': 'www.akretion.com',
 'license': 'AGPL-3',
 'category': 'Generic Modules',
 'description': """Auto installable Module for the compatibility
with the Sale Automatic Workflow and Sale Exception.
Order in exception are ignored by the cron to avoid useless testing
every minutes. Please take care to active the cron "test all draft"
in order to retest some time the order with an exception.
 """,
 'depends': [
     'sale_exceptions',
     'sale_automatic_workflow',
 ],
 'data': [
 ],
 'installable': False,
 'application': False,
 'auto_install': True,
 }
