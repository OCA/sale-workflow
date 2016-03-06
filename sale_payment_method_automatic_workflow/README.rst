Sale Payment Method - Automatic Worflow
=======================================

This module is a glue for **Sale Payment Method** and **Sale
Automatic Workflow**.

When payments are created on a sales orders with
**Sale Payment Method**, **Sale Automatic Workflow** will try to
reconcile them with the invoices.

When a payment method is associated with an automatic workflow, this one
is automatically selected for the sales orders using this method.

Installation
============

As soon as both **Sale Payment Method** and **Sale Automatic Workflow**
are installed, this module is installed and has no special
dependencies.

Configuration
=============

The automatic workflow associated to a payment method can be chosen in
`Sales > Configuration > Sales > Payment Methods`.

Usage
=====

When a payment method is selected on a sales order, if it has an
automatic workflow, the sales order will use it.

The automatic reconcile is done by the **Automatic Workflow Job** cron.

Credits
=======

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Sébastien Beau <sebastien.beau@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
