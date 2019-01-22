.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============
Sale Request
============

This module allows to:

* Create sale orders from sale requisitions and link it to origin sale orders.

Configuration
=============

Any special config is required.

Usage
=====

To create a base sale order:
    * Go to : Sales > Orders > Quotations.
    * Create a new quotations setting as True the field 'Base Sale Order'.
To create a new sale request:
    * Go to : Sales > Orders > Sale Request(s).
    * Create a new sale request setting the corresponding product.
To create a sale order from a sale request:
    * Go to: Sales > Orders > Sale Request(s).
    * Select the sale request.
    * Confirm it.
    * Click on 'Create Sale Order'.
    * Select the corresponding quantities from base sale orders and confirm the wizard.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/oca/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Oscar Garza <oscar.garza@jarsa.com.mx>

Maintainer
----------
This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/sale-workflow <https://github.com/OCA/sale-workflow/tree/12.0/sale_request>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
