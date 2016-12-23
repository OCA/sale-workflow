.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Sale Product set
================

A **product set** is a list of products which end customers aren't aware, this
list is defined by sales manager.

This module aims to help salesman to quickly create several sale order lines
at once in a quotation.

After a *product set* is added to the sale order, each line can be update or
remove as any other sale order lines.

This is differ to packing products as you don't follow *product set* after it
was added to the sale order.

Usage
=====

To use this module, you need to:

* Define a *product set* as sale manager:
    - choose products
    - for each products, define a quantity.
    - Sort *set* lines, this order will be the default when added into the
      quotation

.. image:: /sale_product_set/static/description/product_set.png
    :alt: Set a product set

* On quotation any salesman can click on "Add set" button
  which will open wizard where users can chose a *product set* and quantity
  to add at the end of sale order lines. Order defined in *product set* is
  preserved in sale order.

.. image:: /sale_product_set/static/description/add_set.png
    :alt: Add set to sale order

* Then you can remove or update added lines as any other sale order lines.

.. image:: /sale_product_set/static/description/sale_order.png
    :alt: Sale order

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

*

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_product_set%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.


Contributors
------------

* Clovis Nzouendjou <clovis@anybox.fr>
* Pierre Verkest <pverkest@anybox.fr>
* Denis Leemann <denis.leemann@camptocamp.com>

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
