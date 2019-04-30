.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License LGPL-3

=====================================
Sale Order Action Invoice Create Hook
=====================================

This module adds hook points in sale_order.action_invoice_create() in order
to add more flexibility in the grouping parameters for the creation of
invoices and to give the possibility to take into account draft invoices.

Although the original code has been modified a bit, the logic has been
respected and the method still does exactly the same.

Usage
=====

#. Add dependency of this module
#. Inherit from 'sale.order'
#. Change the _get_invoice_group_key function in order to return more
   grouping fields to take into account when creating a single invoice from
   various Sales Orders.
#. Change the _get_draft_invoices function in order to take into account
   existing draft invoices when creating new ones. This feature is already
   implemented in the module 10.0-sale_merge_draft_invoice.

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

