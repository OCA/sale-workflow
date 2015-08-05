.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Sale Product bundle
===================

This module was written to extend the functionality of sale module
and allow you to set product bundles, which you can quickly add to the sale
order.

After added to the sale order, each line can be update or remove as any other
sale order lines.

This is differ to packing products as you don't follow product bundles after it
was added to the sale order.

Usage
=====

To use this module, you need to:

* Set product bundle as sale manager where you can set:
    - a list of products
    - for each products, a quantity
    - User can set a default bundle lines order that will be keep in sale order

.. image:: /sale_product_bundle/static/description/product_bundle.png
    :alt: Set a product bundle

* On quotation, any salesman can click on "Add bundle in sale order" button
  which will open wizard where users can chose the product bundle and quantity
  to add then at the end of sale order lines.

.. image:: /sale_product_bundle/static/description/add_bundle.png
    :alt: Add bundle to sale order

* Then you can remove or update added lines as any other sale order lines.

.. image:: /sale_product_bundle/static/description/sale_order.png
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
`here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_product_bundle%0Aversion:%201.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Clovis Nzouendjou <clovis@anybox.fr>
* Pierre Verkest <pverkest@anybox.fr>

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
