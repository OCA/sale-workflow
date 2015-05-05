.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Sale line quantity properties based
===================================

*This module allows the calculation of the product quantity on the basis of a
formula that considers the properties specified by the user on the sale order
line and on the quantity (UoS).*

Example
--------

Provided the sale of a given number of pieces (shelves), that may be
’x’ meter long and ’y’ meter large, the formula enables the calculation of the
total area sold expressed in square meters:
    10 [pcs of] (4 m x 0.5 m) shelves = 20 m² of wood

In order to have this function working, it is necessary to have the user
proceeding as follows:

Then s/he shall create properties such as ‘length 4’, ‘width 0.5’.
(Note: this can be more easily achieved by using the modules
'sale_properties_easy_creation' and/or 'sale_properties_dynamic_fields')

Properties must respond the following criteria:
    * Name: ‘length 1’, ‘length 4’, ‘width 0.5’
    * Property Group : either ‘length’ or ‘width’
    * Value : the corresponding quantity (1, 4, 0.5...)

Property 'length 4'
    * Name: ‘length 4’
    * Property Group : ‘length’
    * Value : 4

Property 'width 0.5'
    * Name: ‘width 0.5’
    * Property Group : ‘width’
    * Value : 0.5

After this, the formula 'surface' must be created and associated
to the product:

```
result = float(properties['length']) * float(properties['width']) * qty_uos
```

Upon the registering of the order, the user will apply in the properties field
the desired properties (in this example the ‘lenght 4’ and ‘width 2’), the
needed formula (in this example 'surface') and last the quantity (UoS).

Credits
=======

Contributors
------------

* Alex Comba <alex.comba@agilebg.com>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>

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
