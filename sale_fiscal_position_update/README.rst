.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==========================
Sale order Position Update
==========================

With this module, when a user changes the fiscal position of an sale order, the
taxes and the accounts on all the order lines which have a product are
automatically updated. The order lines without a product are not updated and
a warning is displayed to the user in this case.

Configuration
=============

No specific configuration needed. This module uses the standard
configuration of the fiscal positions.

Usage
=====

Update fiscal position or the partner on the sale order. This will
automatically update the taxes and accounts.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/95/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-invoicing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Mathieu Vatel (Julius Network Solutions)
* Alexis de Lattre <alexis.delattre@akretion.com>
* Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
* Roel Adriaans <roel@road-support.nl>

Do not contact contributors directly about support or help with technical issues.

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
