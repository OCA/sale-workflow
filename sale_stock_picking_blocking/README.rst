.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Sale Stock Picking Blocking
===========================

This module extends the functionality of sales to allow you to block the
creation of deliveries from a sales order and give a reason.

Configuration
=============

To configure this module, you need to:

#. Go to 'Sales > Configuration > Sales > Delivery Block Reason'.
#. Create the different reasons that can lead to block the deliveries of a
   sales order.
#. Add some users to the group 'Release Delivery Block in Sales Orders'.

Additionally, you can set a customer with a 'Default Delivery Block Reason'
policy to add that delivery block to his sales by default:

#. Go to 'Sales > Sales > Customers'.
#. In the 'Sales & Purchases' add a 'Default Delivery Block Reason'.
#. The 'Default Delivery Block Reason' will be added
   automatically when creating a new sales order for the customer.

Usage
=====

To use this module, you need to:

#. Create a new sales order and provide a 'Delivery Block Reason'.
#. Confirm Sale (No delivery would be created).
#. Release Delivery Block when it is time to create the deliveries for
   the sales order.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Lois Rilo <lois.rilo@eficent.com>

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
