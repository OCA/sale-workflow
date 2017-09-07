.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===================
Sale Force Invoiced
===================

This module adds the possibility for users to force the invoice status of the
sales orders to 'Invoiced', even when not all the quantities ordered or
delivered have been invoiced.

This feature useful in the following scenario:

* The customer disputes the quantities to be invoiced for, after the
  products have been delivered to her/him, and you agree to reduce the
  quantity to invoice (without sending a refund).

* When migrating from a previous Odoo version, in some cases there is less
  quantity invoiced to what was delivered, and you don't want these old sales
  orders to appear in your 'To Invoice' list.


Usage
=====

#. Create a sales order and confirm it.
#. Deliver the products/services.
#. Create an invoice and reduce the invoiced quantity. The sales order
   invoicing status is 'To Invoice'.
#. Lock the Sale Order, to change the status of it to 'Done'.
#. Check the field 'Force Invoiced'

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

* Jordi Ballester <jordi.ballester@eficent.com>


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
