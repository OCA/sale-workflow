.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================================
Recalculation of sales order lines prices on demand
===================================================

This module add 2 buttons on sale orders (below sale order lines) that:

* Recalculates the prices of the order lines that contain a product in them.
* Reset product descriptions from current product information.

It is launched manually as a button to get the user decide if he/she wants to
recalculate prices when pricelist is changed or after duplicating a sale order
to update or not sales information.

Usage
=====

Inside a sale order, you can click on "Recalculate prices" to launch a
recalculation of all the prices of the lines, losing previous custom prices.

The second "Reset descriptions" will get descriptions from products, losing
custom descriptions.

.. image:: /sale_order_price_recalculation/static/description/sale_order_price_recalculation.png
    :alt: Sale order price recalculation

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/10.0

Known issues / Roadmap
======================

* In a sale order with lot of lines, the recalculation may slow down, because
  sale general data (amount untaxed, amount taxed...) are recalculated for
  each line.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Pierre Verkest <pverkest@anybox.fr>
* Vicent Cubells <vicent.cubells@tecnativa.com>
* David Vidal <david.vidal@tecnativa.com>

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
