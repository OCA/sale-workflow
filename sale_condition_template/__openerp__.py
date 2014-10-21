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
 "summary": "Condition texts templates on Sale/invoice documents",
 "version": "1.4",
 "depends": ["sale", "account", "base_condition_template"],
 "description": """
Sale/invoive condition
======================

Adds template condition text on sale order and invoice.

Templates are categorized by their position on the document.

Two positions are available:

- before sale order/invoice lines
- after sale order/invoice lines

Texts are copied on the invoice when you will create invoice from sale order.

Contributors
------------

* Nicolas Bessi <nicolas.bessi@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
""",
 "author": "Camptocamp",
 "data": ["account_invoice_view.xml",
          "sale_order_view.xml",
          ],
 "category": "Sale",
 "installable": True,
 "active": False, }
