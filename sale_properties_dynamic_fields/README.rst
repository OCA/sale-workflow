.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Sale properties dynamic fields
==============================

This module allows to dynamically draw properties groups on sale order lines.
That is, if you have a property group 'Length' and set it as
'Draw dynamically', the module will automatically add the x_length field to
the sale order line and visualize it as char field in the form view.
When fill the 'Length' field, the module will update the properties field
(property_ids) according to it.
This allows to set the line's properties through normal fields, instead of
creating new properties or selecting existing properties.

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
