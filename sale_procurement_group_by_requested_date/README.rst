.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :alt: License: AGPL-3

========================================
Sale Procurement Group by Requested date
========================================

This module creates different procurements groups for different requested
dates in a sale order line when the sale order is confirmed.
It depends on sale_sourced_by_line so this module will group procurements 
also by the warehouse in the sale order line.

Installation
============

This module depends on the modules sale_procurement_group_by_line and
sale_sourced_by_line.


Usage
=====

#. Add a requested date for a sale order line.
#. Confirm the sale order

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/10.0


Known issues / Roadmap
======================

This module is compatible with sale_sourced_by_line module by installing
sale_procurement_group_by_requested_date_sale_sourced_by_line. This module
is not compatible with sale_delivery_split_date. A glue module will be needed
to install sale_delivery_split_date and
sale_procurement_group_by_requested_date. This is an already known issue:
https://github.com/OCA/sale-workflow/issues/717#issuecomment-430231334


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback

Credits
=======

Contributors
------------

* Aaron Henriquez <ahenriquez@eficent.com>
* Jordi Ballester <jordi.ballester@eficent.com>
* Darshan Patel <darshan.patel.serpentcs@gmail.com>

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
