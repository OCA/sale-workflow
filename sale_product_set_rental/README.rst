.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Sale Product set rental
=======================

This is an addition to the module 'product set' when used together with 
rental services. Rental services themselves rely on the addon 
sale_start_end_dates. The product sets imported into a sale order
now will receive required info on start and end dates, rental type
and the like.

The new lines in the sale order now automatically have the default
start date and default end date filled in respectively amongst other
line data being prefilled (quantity, rental_qty, number of days).  

 
Usage
=====

Based on respective modules you may add rental product services to
product sets and use these products sets in quotation and sale orders
the same way as standard products.

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

*

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_product_set%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Rudolf Schnapka <rs@techno-flex.de>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
