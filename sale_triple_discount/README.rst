.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Sale Triple Discount
====================

This module allows to have three successive discounts on every sale order
line.

Configuration
=============

To configure this module, you need to:

* set **Discount on lines** group to be able to see discounts on the lines

Usage
=====

Create a new sale order and add discounts in any of the three discount
fields given. They go in order of precedence so discount 2 will be calculated
over discount 1 and discount 3 over the result of discount 2. For example,
let's divide by two on every discount:

Unit price: 600.00 ->

  - Disc. 1 = 50% -> Amount = 300.00
  - Disc. 2 = 50% -> Amount = 150.00
  - Disc. 3 = 50% -> Amount = 75.00

You can also use negative values to make a charge instead of a discount:

Unit price: 600.00 ->

  - Disc. 1 = 50% -> Amount = 300.00
  - Disc. 2 = -5% -> Amount = 315.00

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Nicolas Mac Rouillon <@nicomacr>
* Juan José Scarafía <jjs@adhoc.com.ar>
* Alex Comba <alex.comba@agilebg.com>
* David Vidal <david.vidal@tecnativa.com>
* Simone Rubino <simone.rubino@agilebg.com>
* Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>

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
