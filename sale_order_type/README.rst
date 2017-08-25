.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Sales Order Type
================

This module adds a typology for the sales orders. In each different type, you
can define, invoicing and refunding journal, a warehouse, a sequence,
the shipping policy, the invoicing policy, a payment term, a pricelist
and an incoterm.

You can see sale types as lines of business.

You are able to select a sales order type by partner so that when you add a
partner to a sales order it will get the related info to it.

Configuration
=============

To configure Sale Order Types you need to:

1. Go to **Sales > Configuration > Sales Orders Types**
2. Create a new sale order type with all the settings you want

Usage
=====

* Go to **Sales > Sales Orders** and create a new sale order. Select the new type you have created before and all settings will be propagated.
* You can also define a type for a particular partner if you go to *Sales & Purchases* and set a sale order type.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/10.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_order_type%0Aversion:%20{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Daniel Campos <danielcampos@avanzosc.es>
* Ainara Galdona <ainaragaldona@avanzosc.es>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Samuel Lefever <sam@niboo.be>
* Pierre Faniel <pierre@niboo.be>

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
