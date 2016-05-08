.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=========================
Timesheet details invoice
=========================

Add timesheet details in invoice line to invoices related with timesheets.


Usage
=====

To use this module, you need to:

* Go to *Sales -> Sale Orders* and create a new Sale Order.
* Add line selecting a product with *Invoicing Policy* -> *Delivered
  quantities* and *Track Service* -> *Timesheets on contract*.
  P.E. *Support Contract (on timesheet)*
* Confirm Sale
* Go to *Timesheets -> Activities* and create line with same project of SO
* Go to Sale Order and *Create Invoice*


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/9.0

Known issues / Roadmap
======================

* Recovery states and others functional fields in Contracts.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
sale-workflow/issues/new?body=module:%20
sale_timesheet_description%0Aversion:%20
9.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Carlos Dauden <carlos.dauden@tecnativa.com>

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
