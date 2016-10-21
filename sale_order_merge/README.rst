.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Merge sale orders
=================

This module allows the sale employee to merge draft or confirmed orders
from the same customer.

When orders are merged, draft invoices and unprocessed outgoing pickings
will be merged as well.

Usage
=====

To use this module, you need to go to the main sale order that you want to
merge with other sale orders. If there are any candidates, you will see a
*Merge* button in the header of the sale order form. If you click on this
button, a window will pop-up that has all mergeable sale orders preselected.
Remove the orders that you do not want to merge, and click on the *Merge*
button in the footer of the pop-up window. The main window will then refresh
to the updated main sale order.

The mergeability criteria are defined as follows:

* Same customer, shipping address, warehouse and company.
* Orders must be in status 'Draft Quotation', 'Quotation Sent', 'Waiting Shedule', 'Sale Order', 'Sale to Invoice'.
* Once the order has already been confirmed, only draft orders or confirmed orders with the same invoice policy can be merged.

The criteria can easily be extended in a custom module using method _get_merge_domain of model sale.order

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

Known issues / Roadmap
======================

* Orders with an invoice exception or a picking exception cannot be merged.
* If prepaid sale orders with confirmed invoices are merged, procurement will not be postponed until all the invoices are paid. Instead, it will start when the original invoice of the main order has been paid.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Stefan Rijnhart <stefan@opener.amsterdam>

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
