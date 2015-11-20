.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Sale Order Partial Advance
===========================

This module was written to extend the sale advance management. It allows to
use an advance amount progressively when you invoices only some order lines.

Example:
    You create a sale order with 4 differents products for a total amount of 2000.
    The customer pays an advance of 600. All the products will not be delivered 
    in the same time and, once you invoice the first delivery,
    you want to keep a part of the advance as warranty and only deduct 400
    from the 600 paid.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/sale_workflow/issues/new?body=module:%20sale_order_partial_advance%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Cédric Pigeon <cedric.pigeon@acsone.eu>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.