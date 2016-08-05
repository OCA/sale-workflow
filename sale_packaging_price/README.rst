.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/lgpl
    :alt: License: LGPL-3

====================
Sale Packaging Price
====================

This module extends the functionality of sale workflow and allows you to assign
a selling price of a complete package. This price is split for having the price
unit according the number of pieces that fit in that packaging, so there can be
rounding issues to get the exact price that are warned if happens. It also adds
a field to set the package material.

Configuration
=============

To configure this module, you need to:

#. Go to *Inventory > Configuration > Settings*.
#. Enable *Traceability > Packages > Record packages used on packing: pallets,
   boxes, ...*
#. Enable *Products > Packaging Methods > Manage available packaging options
   per products*.
#. *Apply*.

Usage
=====

First, ensure you have permissions for *Technical Settings / Manage Product
Packaging*.

Then, to use this module, you need to:

#. Go to *Inventory > Inventory Control > Products*.
#. Edit or create a product.
#. Go to *Inventory* tab.
#. Under *Packaging* you can create packages for this product.

To batch managing of packages, you need to:

* Go to *Inventory > Inventory Control > Packagings*.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/9.0

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

* Rafael Blasco <rafabn@antiun.com>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Carlos Dauden <carlos@incaser.es>
* Sergio Teruel <sergio@incaser.es>
* Jairo Llopis <jairo.llopis@tecnativa.com>

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
