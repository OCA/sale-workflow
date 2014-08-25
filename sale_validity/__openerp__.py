# -*- coding: utf-8 -*-
#
#
#    Author: Jacques-Etienne Baudoux
#    Copyright 2013 Camptocamp SA
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

{"name": "Sales Quotation Validity Date",
 "version": "8.0.7.0.0",
 "depends": ["sale"],
 "author": "Camptocamp,Odoo Community Association (OCA)",
 "category": "Sales",
 "website": "http://www.camptocamp.com",
 "description": """
Sale order validity date
========================

Add a validity date on the sales quotation defining
until when the quotation is valid.

A default validity duration (in days) can be configured on the company.

""",
 'data': [
     "view/sale_order.xml",
     "view/company_view.xml",
 ],
 'test': [
     'test/sale_validity.yml',
 ],
 'installable': True,
 }
