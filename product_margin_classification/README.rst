.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3


=============================
Product Margin Classification
=============================

This module is designed to extend Sale Price computation in Odoo.

This module add a new model 'Margin Classifications' linked to Product Templates.

A margin classification has a margin field (and fields to manage rounding method, like Pricelist Item model).

If product has a margin classification defined, an extra field
'Theoritical Price' is displayed, based on the Margin and the Cost Price.

If the theoritical price is not the same as the sale price, a button is
available to change sale price.

.. image:: /product_margin_classification/static/description/product_template_form.png

On the Margin classification Form, user can change computation fields.
(Margin, Rounding method, ...) 
Three buttons are available to apply theoritical prices to all products, or
only for products that have a too big or too little real margin.

.. image:: /product_margin_classification/static/description/margin_classification_form.png

User can so see easily products with incorrect margins and fix them massively :

.. image:: /product_margin_classification/static/description/margin_classification_tree.png

Note
====

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

Once Installed :

* Go to : 'Sale' / 'Products' / 'Margin Classifications'
* Create new classifications
* Set classification to your products

Credits
=======

Contributors
------------

* Sylvain LE GAL <https://twitter.com/legalsylvain>
