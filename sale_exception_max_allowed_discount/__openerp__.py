# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Eficent (<http://www.eficent.com/>)
#              <contact@eficent.com>
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
{'name': 'Sale exception maximum allowed discount',
 'version': '1.0',
 'author': "Eficent,Odoo Community Association (OCA)",
 'maintainer': 'Eficent',
 'category': 'sale',
 'license': 'AGPL-3',
 'complexity': "normal",
 'depends': ['sale_exceptions'],
 'website': 'http://www.eficent.com',
 'description': """
Sale exception maximum allowed discount
=======================================

This module was created to extend the sales process.

A sales user cannot approve a sales quotation if any of the items contain a
sales discount % above the maximum allowed, for a product that is subject to
this validation.

Installation
============

No specific installation steps are required.

Configuration
=============

No specific configuration steps are required.

Usage
=====

The user can define in the product 'Sales' tab if the maximum applicable
discount should be checked, and can and set the maximum discount as a
percentage.

Known issues / Roadmap
======================

No issues have been identified with this module.

Credits
=======

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
""",
 'data': [
     "data/data.xml",
     "view/product_view.xml",
     ],
 'demo': [],
 'test': ['test/max_discount_exceeded.yml'],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False,
 }
