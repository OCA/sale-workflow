# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Authors: Raphaël Valyi, Renato Lima
#    Copyright (C) 2011 Akretion LTDA.
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
{'name': 'Sale Exceptions',
 'summary': 'Custom exceptions on sale order',
 'version': '8.0.1.0.0',
 'category': 'Generic Modules/Sale',
 'description': """
Sale Exceptions
===============

This module allows you attach several customizable exceptions to your
sale order in a way that you can filter orders by exceptions type and fix them.

This is especially useful in an order importation scenario such as with
the base_sale_multi_channels module, because it's likely a few orders have
errors when you import them (like product not found in Odoo, wrong line
format etc...)

Contributors
------------

* Raphaël Valyi <raphael.valyi@akretion.com>
* Renato Lima <renato.lima@akretion.com>
* Sébastien BEAU <sebastien.beau@akretion.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>

""",
 'author': "Akretion,Odoo Community Association (OCA)",
 'website': 'http://www.akretion.com',
 'depends': ['sale'],
 'data': ['sale_workflow.xml',
          'sale_view.xml',
          'sale_exceptions_data.xml',
          'wizard/sale_exception_confirm_view.xml',
          'security/ir.model.access.csv',
          'settings/sale.exception.csv'],
 'installable': True,
 }
