.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

==========================================
Easing properties input in sale order line
==========================================

This modules simplifies the input of properties in the sale order line and
other places.

For instance, in the many2many field 'property_ids', it allows the user to
digit 'width 0.5' and the system will automatically create a property of group
'width' with value '0.5'

It also adds the model 'mrp.property.formula', to be used by computations based
on properties.
Used by modules like 'sale_line_price_properties_based' and
'sale_line_quantity_properties_based'

Configuration
=============

The user needs to enable **Properties on lines** setting in
**Technical Settings** section.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_properties_easy_creation%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Alex Comba <alex.comba@agilebg.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
