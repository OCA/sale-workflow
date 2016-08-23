.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Sale Automatic Workflow - Payment Mode
======================================

This module is a glue for **Account Payment Sale** (of the OCA/bank-payment
project) and **Sale Automatic Workflow**.

When a payment mode is associated with an automatic workflow, this one
is automatically selected for the sales orders using this method.

Installation
============

As soon as both **Account Payment Mode** and **Sale Automatic Workflow**
are installed, this module is installed.

Configuration
=============

The automatic workflow associated to a payment mode can be chosen in
the configuration of the payment modes in the Invoicing configuration menu.

Usage
=====

When a payment mode is selected on a sales order, if it has an
automatic workflow, the sales order will use it.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Sodexis <dev@sodexis.com>

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
