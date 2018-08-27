.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

===================================
Sale line quantity properties based
===================================

This module allows the calculation of the product quantity on the basis of a
formula that considers the properties specified by the user on the sale order
line and on the quantity (UoS).

Example
-------

Provided the sale of a given number of pieces (shelves), that may be
’x’ meter long and ’y’ meter large, the formula enables the calculation of the
total area sold expressed in square meters:

    10 [pcs of] (4 m x 0.5 m) shelves = 20 m² of wood

In order to have this function working, it is necessary to have the user
proceed as follows:

Then s/he shall create properties such as ‘length 4’, ‘width 0.5’.
(Note: this can be more easily achieved by using the modules
'sale_properties_easy_creation' and/or 'sale_properties_dynamic_fields')

Properties must respect the following criteria:
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


.. code-block:: python

  result = float(properties['length']) * float(properties['width']) * qty_uos

Upon the registering of the order, the user will apply in the properties field
the desired properties (in this example the ‘length 4’ and ‘width 2’), the
needed formula (in this example 'surface') and last the quantity (UoS).

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_line_quantity_properties_based%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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
