# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi
#    Copyright 2013-2014 Camptocamp SA
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
{"name": "Sale/invoice condition",
 "version": "1.3",
 "depends": ["sale", "account"],
 "description": """Adds predefine header and footer text on sale order and
     invoice.
Texts are passed in the invoice when sale order is transformed into invoice""",
 "author": "Camptocamp",
 "data": ["account_invoice_view.xml",
          "sale_order_view.xml",
          "condition_view.xml"],
 "category": "Sale",
 "installable": True,
 "active": False, }
