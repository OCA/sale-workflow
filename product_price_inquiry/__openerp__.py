# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
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
    'name': 'Product Sale Price Inquiry',
    'version': '1.0',
    'author': 'Elico Corp, Odoo Community Association (OCA)',
    'website': 'http://www.elico-corp.com',
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Product Sale Price Inquiry
==========================

This module adds a wizard to quickly search product prices
based on product quantities.

Usage
=====

To use this module, you need to:

 * go to Sales -> Configuration -> Pricelists, choose the pricelist
    you want it to be visible for price inquiry.
 * go to Sales -> Product Price Inquiry, choose product, product quantity
    and pricelist, and click button:inquiry to have the unit price.

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

 * ...

Credits
=======

Contributors
------------

* Alex Duan <alex.duan@elico-corp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
    whose mission is to support the collaborative development of Odoo features
    and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
    """,
    'depends': ['product'],
    'category': '',
    'sequence': 16,
    'demo': [],
    'data': [
        'product_price_inquiry_view.xml',
    ],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
