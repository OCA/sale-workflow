.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License LGPL-3

=========================
Sale Invoice Group Method
=========================

This module allows you to combine several Sales Orders into a single invoice,
if they meet the split criteria defined by the 'Invoice Group Method'.

The split criteria is defined in the 'Invoice Group Method' by a combination
of fields of the Sales Order. 'Invoice Address', 'Currency' and 'Payment Term'
are always included.

You can assign a default 'Invoice Group Method' to customers, so that it will
be proposed on their orders.

When no Invoice Group Method is defined in a Sales Order, the standard
approach will be used, which groups by Sales Order.

Note: Existing draft invoices are not considered in the process of grouping.
However, you can find the feature implemented in ``sale_merge_draft_invoice``
from sale-workflow repository.

Configuration
=============

#. Go to 'Sales / Configuration / Invoice Group Method'
#. Create an Invoice Group Method and choose the fields of the Sales Order
   that should be equal in that particular grouping method, for their orders
   to be merged into the same invoice. For example, create the Invoice Group
   Method 'By Customer' and select the field 'Customer').

Usage
=====

Update customers
----------------

#. Go to 'Sales / Sales / Customers'
#. Choose a customer and go to 'Sales & Purchases' page.
#. Update the 'Default Invoice Group Method'

Create a Quote / Sale Order
---------------------------

#. Go to 'Sales / Sales / Quotations'.
#. Create a new Quote and inside the 'Other Information' page select an
   option from the field 'Invoice Group Method'. If the customer had a
   default, it will have been provided already.
#. Complete the Quote as usual.

Create Invoices
---------------

#. Go to 'Sales / Sales / Sales Orders'.
#. Select all the sales orders with status 'To invoice'.
#. Go to 'Action' and click 'Invoice Order'. As a result, draft invoices will be
   created for the selected Sales Orders, consolidating them according to the
   Invoice Group Method defined.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/purchase-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Jordi Ballester Alomar <jordi.ballester@eficent.com>
* Roser Garcia <roser.garcia@eficent.com>

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
