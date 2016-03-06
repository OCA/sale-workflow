.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

====================
Sale Packaging Price
====================

This module was written to extends the functionality of sale workflow
and allow you to assign a selling price of a complete package.
This price is split for having the price unit according the number of pieces
that fits in that packaging, so there can be rounding issues to get the exact
price that are warned if happens. It also adds a field to set the package
material.

Configuration
=============

To configure this module, you need to:

* go to warehouse config and check 'Use packages: pallets, boxes, ...' and
  'Allow to define several packaging methods on products'

Usage
=====

To use this module, you need to:

* go to product and into inventory tab you can add new packages with a
  sale price

* This module also adds a new entry into product menu called 'Packaging' to
  add quickly combinations packages

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale_workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/sale_workflow/issues/new?body=module:%20sale_packaging_price%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Rafael Blasco <rafabn@antiun.com>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Carlos Dauden <carlos@incaser.es>
* Sergio Teruel <sergio@incaser.es>

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
