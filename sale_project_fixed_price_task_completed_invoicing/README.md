.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Sale Project Fixed Price Task Completed Invoicing
=================================================

The main goal of this module is to add the possibility to link a sale.order.line
to a project.task considering the delivery.
Unless sale_timesheet, the quantity shipped won't be linked to a Timesheet nor
to the time spent on the task. The price is fixed on the sale.order.line and it
will be considered as shipped once the task is accomplished.

Usage
=====

Create a product with product.type 'Service' and track_service 'Completed Task'.

Use it in a Sale Order. Once you validate the Sale Order, it will create a linked
project and task.

Once the task is finished, on the form view of the corrisponding task click on the
button 'Invoiceable'. The linked sale.order.line will be considered as shipped.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Denis Leemann <denis.leemann@camptocamp.com>


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
