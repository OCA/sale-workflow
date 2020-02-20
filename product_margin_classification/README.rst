.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3


=============================
Product Margin Classification
=============================

This module is designed to extend Sale Price computation in Odoo.

This module add a new model 'Margin Classifications' linked to Product Templates.

A margin classification has a 'Profit Margin' field and extra fields to manage
computation method, like in Pricelist Item model (Markup Rate, Rounding and Surcharge fields)

If product has a margin classification defined and the theoretical price is
not the same as the sale price, an extra field 'Theoretical Price' is
displayed, based on the Margin Classification and a button is available to
change sale price.

.. image:: /product_margin_classification/static/description/product_template_form.png

On the Margin classification Form, user can change computation fields.
(Margin, Rounding method, ...) 
Three buttons are available to apply theoretical prices:
* to all products, 
* only for products that are too expensive
* only for products that are too cheap

.. image:: /product_margin_classification/static/description/margin_classification_form.png

User can so see easily products with incorrect margins in the tree views, and in the menu:

.. image:: /product_margin_classification/static/description/margin_classification_tree.png

Note
====

This module use both [Markup](https://en.wikipedia.org/wiki/Markup_(business))
and [Profit Margin](https://en.wikipedia.org/wiki/Profit_margin) concepts.

You could be interested by native Pricelist functionnalities, setting sale
prices based on Cost prices. The main problem of this design is that sale price
change automaticaly when cost price changes, that is not desired in some user
cases. For exemple, if you have a shop, you want to changes sale prices when
customers is not in the shop, and after having changed labels in the shop.


Installation
============

Normal installation.

Configuration
=============

Once Installed

* Go to : 'Sale' / 'Products' / 'Margin Classifications'
* Create new classifications
* Set classification to your products

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.


Contributors
------------

* Sylvain LE GAL <https://twitter.com/legalsylvain>

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
