.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Sale Timesheet Lock Invoiced
============================

Forbids to update/delete a timesheet line if it has been invoiced.
*sale_timesheet* module only forbids to edit some fields. This module will
block any update and deletion of invoiced lines.

Usage
=====

To use this module, you need to:

#. Create a sale order with a timesheet generation
#. Confirm the sale
#. Create some timesheet lines in the sale order's tasks
#. Invoice the SO based on the invoiceable lines
#. Validate the invoice
#. Try to update/delete the previously created timesheet lines

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/11.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Benjamin Willig <benjamin.willig@acsone.eu>

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
