.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============================
Security rules for sales teams
==============================

This module sets different permissions levels for accessing sales and CRM
records based on the sales team: customers, sales orders, leads, opportunities,
phone calls and sales teams.

It also handles the propagation of the sales team from commercial partners to
the contacts, which standard doesn't make.

Installation
============

At installation time, this module sets in all the contacts that have the sales
team empty the sales team of the parent. If you have a lot of contacts, this
operation can take a while.

Configuration
=============

On the user configuration (Configuration > Users > Users), select in the
*Sales Team* section the option "See only own team". Then, the documents
mentioned before will be filtered out to have only those belonging to the
teams the user belongs to.

This is complementary to the "Sales" level access, but sometimes can be
incoherent depending on the combination chosen. If you chose "See Own Leads"
on *Sales* section, marking or unmarking the sales team check will be
irrelevant, because the most restricting level, which is the sales one, will
prevail.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Known issues/Roadmap
====================

* This module is designed for supporting only sales part, so someone that has
  access to other Odoo parts (for example, an accountant), shouldn't have
  this new permission, or some access errors will be found when seeing invoices
  and other documents. A *sales_team_security_account* bridge module can be
  done for fixing this case, but not in the case of for example warehouse.

Credits
=======

Contributors
------------

* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
