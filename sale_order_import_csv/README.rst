.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Sale Order Import CSV
=====================

This module adds support for the import of electronic RFQ or orders as CSV file. The structure of the CSV file is the same as for the `Dilicom <https://dilicom-prod.centprod.com>`_ plateform (the main plateform to order books in France). It contains 2 columns:

* the 1st column contains the product code (EAN13 or any other product code),
* the 2nd column contains the product quantity, using '.' (dot) as decimal separator and without any thousand separator.

It shouldn't have any header line and use semi-colon as field separator. The CSV file is expected to use UTF-8 encoding ; but as product codes rarely use non-ASCII caracters, the file is identical to an ASCII-encoded file.

Example of an order CSV file:

.. code::
  5410228193449;2
  5449000054227;10
  5449000111715;5

As the CSV order doesn't contain any pricing information, the prices are always computed from the pricelist of the customer.

If you want to export an Odoo purchase order as a CSV file, you can use the module *purchase_dilicom_csv* available `on Akretion's Github <https://github.com/akretion/dilicom>`_.

Configuration
=============

No configuration is needed.

Usage
=====

Read the description of the *sale_order_import* module for a detailed usage description. As the CSV file doesn't contain any identification of the customer, when you import a CSV file, the wizard will ask you to select the customer. If you want to test the import of a CSV order and your Odoo database is loaded with the demo data, you can import the file *sale_order_import_csv/tests/files/order_file_test1.csv*.

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
