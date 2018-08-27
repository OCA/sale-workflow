Sale Payment Method
===================

It adds a payment method on the sales orders and allow to register
payments entries on sales orders.

This module is low level and works well with the following modules:

* **Sale Automatic Worflow** and **Sale Payment Method - Automatic Workflow**
  the payments created with this module will be automatically reconciled
  with the invoices of the sales orders.
* Sale Quick Payment: allows to create the payments with a button on the
  sales orders.

Also, the e-commerce connectors such as the **Magento Connector** or
**Prestashop Connector** use it to create the external payments.

Installation
============

Nothing special is required.

Configuration
=============

The payment methods can be configured in **Sales > Configuration >
Sales > Payment Methods**.

Usage
=====

A new field on sales orders allow to select the payment method used on
this sales order.

Known issues / Roadmap
======================

 * It accepts only one method per sale order.

Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Sébastien Beau <sebastien.beau@akretion.com>
* Arthur Vuillard <arthur.vuillard@akretion.com>
* Jan-Philipp Fischer <jan-philipp.fischer@greencoding.de>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
