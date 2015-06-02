Sale Rental
===========

With this module, you can rent products with Odoo. This module supports:

* regular rentals,
* rental extensions,
* sale of rented products.

Configuration
=============

In the menu *Sales > Products > Product Variants*, on the form view
of a stockable product or consumable, in the *Rental* tab, there is a
button *Create Rental Service* which starts a wizard to generate the
corresponding rental service.

In the menu *Warehouse > Configuration > Warehouses*, on the form view
of the warehouse, in the *Technical Information* tab, you will see two
additional stock locations: *Rental In* (stock of products to rent) and
*Rental Out* (products currently rented). In the *Warehouse Configuration* tab,
make sure that the option *Rental Allowed* is checked.

To use the module, you need to have access to the form view of sale
order lines. For that, you must add your user to one of these groups:

* Manage Product Packaging
* Properties on lines

Usage
=====

In a sale order line (form view, not tree view), if you select a rental
service, you can :

* create a new rental with a start date and an end date: when the sale
  order is confirmed, it will generate a delivery order and an incoming
  shipment.
* extend an existing rental: the incoming shipment will be postponed to
  the end date of the extension.

In a sale order line, if you select a product that has a corresponding
rental service, you can decide to sell the rented product that the
customer already has. If the sale order is confirmed, the incoming
shipment will be cancelled and a new delivery order will be created with
a stock move from *Rental Out* to *Customers*.

Please refer to `this screencast <https://www.youtube.com/watch?v=9o0QrGryBn8>`
to get a demo of the installation, configuration and use of this module
(note that this screencast is for Odoo v7, not v8).

Known issues / Roadmap
======================

This module has the following limitations:

 * No support for planning/agenda of the rented products
 * the unit of measure of the rental services must be *Day* (the rental per hours / per week / per month is not supported for the moment)

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
