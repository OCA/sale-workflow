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
{"name": "Base condition template",
 "summary": "Condition texts templates on documents",
 "version": "1.0",
 "depends": ["base"],
 "description": """
Base condition template
=======================

Add a new model to define templates of condition text to print on
documents.


Templates are categorized by their position on the document.

Two positions are available:

- before document lines
- after document lines

This module is the base module for following modules:

* sale_condition_template
* purchase_condition_template

Contributors
------------

* Nicolas Bessi <nicolas.bessi@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
""",
 "author": "Camptocamp",
 "data": ["condition_view.xml"],
 "category": "Sale",
 "installable": True,
 "active": False, }
