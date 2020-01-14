.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=========================================
Sale Procurement Group by Commitment Date
=========================================

This module creates different procurements groups for different commitment
dates in a sale order line when the sale order is confirmed.

Installation
============

This module depends on the modules sale_procurement_group_by_line and
sale_order_line_date.

Usage
=====

#. Add a requested date for a sale order line.
#. Confirm the sale order.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/12.0


Known issues / Roadmap
======================

This module is not compatible with sale_delivery_split_date. A glue module will be needed
to install sale_delivery_split_date and sale_procurement_group_by_commitment_date.
This is an already known issue:
https://github.com/OCA/sale-workflow/issues/717#issuecomment-430231334


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

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Aaron Henriquez <ahenriquez@eficent.com>
* Jordi Ballester <jordi.ballester@eficent.com>
* Darshan Patel <darshan.patel.serpentcs@gmail.com>

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
