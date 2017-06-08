.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Sale Order Import
=================

This module adds support for the import of electronic RFQ or orders. This module provides the base methods to import electronic orders ; it requires additionnal modules to support specific order formats:

* module *sale_order_import_csv*: adds support for CSV orders,

* module *sale_order_import_ubl*: adds support for `Universal Business Language (UBL) <http://ubl.xml.org/>`_ RFQs and orders as:

  - XML file,
  - PDF file with an embedded XML file.

Configuration
=============

No configuration is needed.

Usage
=====

This module adds a wizard in the sale menu named *Import RFQ or Order*. This wizard will propose you to select the order or RFQ file. Depending on the format of the file (CSV, XML or PDF) and the type of file (RFQ or order), it may propose you additionnal options.

When you import an order, if there is a quotation in Odoo for the same customer, the wizard will propose you to either update the existing quotation or create a new order (in fact, it will create a new quotation, so that you are free to make some modifications before you click on the *Confirm Sale* button to convert the quotation to a sale order).

Once the RFQ/order is imported, you should read the messages in the chatter of the quotation because it may contain important information about the import.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

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
