.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :alt: License: AGPL-3

========================================
Sale Procurement Group by Requested date
========================================

This module creates different procurements groups for different requested
dates in a sale order line when the sale order is confirmed.
It depends on sale_sourced_by_line so this module will group procurements
the warehouse in the sale order_line also.

Installation
============

This module depends on the modules sale_procurement_group_by_line and
sale_sourced_by_line.


Configuration
=============

No special configuration is required.

Usage
=====

* Add a requested date for a sale order line.
* Confirm the sale order

Credits
=======

Contributors
------------

* Aaron Henriquez <ahenriquez@eficent.com>
* Jordi Ballester <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
