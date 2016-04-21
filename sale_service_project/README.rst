.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

====================
Sale Service Project
====================

This module helps you to manage task created from sales order, let you choose
if you wants to invoice from sale order or from task, and helps you to control
with sale order must be invoiced or not depending if the task have been done or
not.

This module adds the option to assign materials and/or works to a service
product type which serve as a template transferring this information to the
line order which may be changed.

This module extends the functionality of the *sale_service* module creating a
new project for each order adding materials and works informed on the order
line to the generated task.

Usage
=====

To use this module, you need to:

#. Go to Sales -> Products and create a product with type Service, check also
   option 'Create task automatically'.
   Now you can add task works and materials for this product.
   You can compute the total price based in all materials and task works
   assigned. In the wizard you must select the product that has assigned
   price's work hour.
#. Go to Sales -> Sales Orders and create new with a service product with works
   or/and materials which can be modified in each line.
#. Print Sale Order to view the new detailed report. If you don't want detail,
   you can disable *Print materials and works*.
#. Assign a Analytic Account or check *invoice_on_timesheets* in Other
   Information tab. (Default value to this field is the same that analytic
   account have assigned, but it can be modified. In the new project created,
   the invoice_on_timesheets field will have same value that the Sale Order.)
   If invoice_on_timesheets field is checked this SO will be invoiced from
   tasks or analytic lines.
#. Confirm Sale Order. A new child project will be created and assigned to the
   Sale Order.
#. Manage the task/s created and invoice when task is closed.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
sale-workflow/issues/new?body=module:%20
sale_service_project%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Rafael Blasco <rafael.blasco@tecnativa.com>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Carlos Dauden <carlos.dauden@tecnativa.com>
* Sergio Teruel <sergio.teruel@tecnativa.com>
* Antonio Espinosa <antonio.espinosa@tecnativa.com>

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
