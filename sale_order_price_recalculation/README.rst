===================================================
Recalculation of sales order lines prices on demand
===================================================

.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

This module adds a button on sale orders below pricelist that recalculates the
prices of the order lines that contain a product in them.

It is launched manually as a button to get the user decide if he/she wants to
recalculate prices when pricelist is changed.

Usage
=====

Inside a sale order, you can click in any moment a button called
"(Recalculate prices)", that is next to the pricelist selection, to launch
a recalculation of all the prices of the lines, losing previous custom prices.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

Known issues / Roadmap
======================

* In a sale order with lot of lines, the recalculation may slow down, because
  sale general data (amount untaxed, amount taxed...) are recalculated for
  each line.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_order_price_recalculation%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
