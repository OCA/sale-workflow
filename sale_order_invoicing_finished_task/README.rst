.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

==================================
Sale Order Invoicing Finished Task
==================================

The requirement of this module is to add in the task the possibility to indicate if it is invoiceable o not.

Usage
=====

To use this module, you need to:


1. Go to Sales -> Product and create a service product

2. In the product go to Invoicing tab and select (1) An invocing policy (2) Track
   service must be create a task and tack hours (3) Set Invoicing finished task
   checkbox and save


   .. image:: static/description/product_view_invoicefinishedtask.png


3. Go to Sales -> Sale orders -> Create a new one. Add a customer y the product
   you have created
4. Confirm the sales order, it will create you a proyect and a task
5. Go to the task and you will find a smartbutton called Not invoiceable, when
   you press the button you will indicate that the task can be invoiced

   .. image:: static/description/task_view_invoicefinishedtask.png

You can try it in:

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/167/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/
  blob/master/template/module/static/description/icon.svg>`_.


Contributors
------------

* Denis Leemann <denis.leemann@camptocamp.com> 
* Sergio Teruel <sergio.teruel@tecnativa.com>
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
