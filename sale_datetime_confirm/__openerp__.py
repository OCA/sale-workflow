# -*- coding: utf-8 -*-
###############################################################################
#
#    Module for OpenERP
#    Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Benoît GUILLOT <benoit.guillot@akretion.com>
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
###############################################################################
{'name': 'Sale Datetime Confirm',
 'summary': 'Change confirmation date type on sale order',
 'version': '1.0',
 'category': 'Generic Modules/Sale',
 'description': """
Sale Datetime Confirm
===============

This module changes the type of the field date_confirm from date to datetime.

""",
 'author': "Akretion,Odoo Community Association (OCA)",
 'website': 'http://www.akretion.com',
 'depends': ['sale'],
 'data': [
     'sale_view.xml',
     ]
 'installable': True,
 }
