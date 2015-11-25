.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

==============================
Sale properties dynamic fields
==============================

This module allows to dynamically display properties groups on sale order lines.
That is, if you have a property group 'Length' and set it as
'Display dynamically', the module will automatically add the x_length field to
the sale order line and visualize it as char field in the form view.
When fill the 'Length' field, the module will update the properties field
(property_ids) according to it.
This allows to set the line's properties through normal fields, instead of
creating new properties or selecting existing properties.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_properties_dynamic_fields%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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
