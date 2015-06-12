.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

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
