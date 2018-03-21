.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
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

#. Go to **Sales > Configuration > Sales Orders Types**
#. Create a new sale order type with all the settings you want

Usage
=====

#. Go to **Sales > Sales Orders** and create a new sale order. Select the new
   type you have created before and all settings will be propagated.
#. You can also define a type for a particular partner if you go to *Sales &
   Purchases* and set a sale order type.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* `Vermon <http://www.grupovermon.com>`_

  * Carlos Sánchez Cifuentes <csanchez@grupovermon.com>

* `AvanzOsc <http://avanzosc.es>`_

  * Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
  * Ana Juaristi <anajuaristi@avanzosc.es>
  * Daniel Campos <danielcampos@avanzosc.es>
  * Ainara Galdona <ainaragaldona@avanzosc.es>

* `Agile Business Group <https://www.agilebg.com>`_

  * Lorenzo Battistini <lorenzo.battistini@agilebg.com>

* `Niboo <https://www.niboo.be/>`_

  * Samuel Lefever <sam@niboo.be>
  * Pierre Faniel <pierre@niboo.be>

* `Tecnativa <https://www.tecnativa.com>`_

  * Pedro M. Baeza <pedro.baeza@tecnativa.com>
  * David Vidal <david.vidal@tecnativa.com>

Do not contact contributors directly about support or help with technical issues.

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
