.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Sales Payment Term Interests
============================

This module allows to compute interest fees based on payment terms and
to add a line in the sales orders with the computed amount.

Installation
============

To install this module, you need to:

 * Install the `sale_order_interest` module is the only things to do.

Configuration
=============

To configure this module, you need to:

 * Go to *Invoicing > Configuration > Payment Terms*
 * On the lines of the payment terms, you can configure an interest
   rate. It is based on the number of days.

Usage
=====

To use this module, you need to:

 * When a sales order has a payment term with interest fees, a line will
   automatically be added when it is saved. A button next to the
   payment terms allows to update it directly.

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

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
