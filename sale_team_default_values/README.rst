.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Sale Teams Default Values
=========================

Before Odoo 8.0, the sale.shop object contained some defaults for the sale
process that were propagated to sale orders and invoices.

The shop was removed in 8.0, so this module uses the Sale Team as a
replacement. Now a new tab in the Sale Team contains defaults that will be
propagated to orders and invoices.

This module is useful both to set up defaults for manual use, and also for
interfaces with external systems (e-commerce, ESBs, etc) were orders need to be
validated automatically.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

Configuration
=============

To configure the module, open a Sale Team and fill in the fields in the
"Default Values" tab. None of them is required.

Usage
=====

In a Sale Order, choose one of the Sale Teams where you configured default
values. All the default values that were given will be applied to the current
Sale Order. The Journal field is only relevant to invoices. The Journal from
the chosen Sale Team will be used when generating an invoice from the Order.

If a default value is left empty in the Sale Team, than no action will be done:
existing values in the Sale Order will not be removed.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale_workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
sale_workflow/issues/new?body=module:%20
sale_team_default_values%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>

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
