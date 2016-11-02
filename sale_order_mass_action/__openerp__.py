# -*- coding: utf-8 -*-
##############################################################################
#
#    Sale - Sale Order Mass Action module for Odoo
#    Copyright (C) 2015-Today GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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
    'name': 'Sale Orders Mass Action',
    'version': '7.0.0.1.0',
    'author': "GRAP,Odoo Community Association (OCA)",
    'website': 'http://www.grap.coop',
    'license': 'AGPL-3',
    'category': 'Sales',
    'description': """
Sale Orders Mass Action
=======================

Facilities to perform mass action on Sale Orders:

* A wizard which allows on multiple Sale Orders at a time to:
    * confirm Sale Orders;

Known issues / Roadmap
======================

* Possibility to create invoices for many Sale Orders at a time;

Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

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
    'depends': [
        'sale',
    ],
    'data': [
        'wizard/sale_order_mass_action_view.xml',
    ],
}
