.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Sale Manual Delivery
=====================

The goal of this module is to allow the manual creation of delivery slips. If activated,
a sale order won't direcly impact directly the stock. It will not make a reservation on the stock.
It allows the delivery and the impact on stock to be done manually when needed.
The goal is to be used on long term projects where not all the material is shipped at once.
As you make many shipments, every time you make a new delivery, you can choose an new carrier as well
as a planned date. A wizard helps you to chose what to deliver by showing you how much you already 
planned to ship.

In many cases, is the warehouse user the one that goes to the SO and ship. This
usually is a pain because there are many shipments and finding the proper one
is complicated. For those reasons it is very useful to have a menu in Inventory
to create the delivery directly and also do it at sale order line level. 


Known issues / Roadmap
======================
* Add Screenshots


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.


Contributors
------------

* Denis Leemann <denis.leemann@camptocamp.com>
* Joel Grand-Guillaume <joel.grandguillaume@camptocamp.com>


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
