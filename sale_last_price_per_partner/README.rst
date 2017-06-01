.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

===========================
Sale last price per partner
===========================

The former last_sale_price module ported to version 10

Add price, quantity and date of a product of the last time it was sold to
a partner.

In order to let the salesman know if a customer already ordered a product.
And to give him hint about what price he should propose.
That information is shown next to the price in Sale Order's line Form.

Only Sale Orders' lines in state Confirmed and Done are considered to
compute those fields.

If multiple Sale Order lines for the same partner where made on the same
date for the same product, the sum of all quantity and the average price
will be displayed.


Usage
=====

To use this module, you need to:

   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/10.0

For further information, please visit:

* https://www.odoo.com/forum/help-1


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback


Credits
=======

Contributors
------------
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Anar Baghirli <a.baghirli@mobilunity.com>

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
