.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Sales Payment Term Interests
============================

This module allows to compute interest fees based on payment terms and
to add a line in the sales orders with the computed amount.

Installation
============

To install this module, you need to:

 * Install the `sale_payment_term_interest` module is the only things to do.

Configuration
=============

To configure this module, you need to:

 * Go to *Invoicing > Configuration > Payment Terms*
 * On the lines of the payment terms, you can configure an annual interest
   rate. The interest fee is based on the number of term days.

Usage
=====

To use this module, you need to:

 * When a sales order has a payment term with interest fees, a line will
   automatically be added when it is saved. A button next to the
   payment terms allows to update it directly.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_payment_term_interest%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
whose mission is to support the collaborative development of Odoo
features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
