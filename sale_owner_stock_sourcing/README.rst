.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Sale Owner Stock Sourcing
==========================

This module allows you to choose for every sale order line the owner of the
stock that will be dispatched.  By choosing an owner, the generated deliveries
will then look for stock belonging to the specified partner.  If none is
available, then the picking will be waiting availability until stocks with
proper ownership are replenished.

Specifying an owner on a line forces to use the stock of this owner.  Leaving
the owner empty allows to use stock (quant) without owner.

Note: pickings and moves both have an owner field. Here we only propagate the
owner to moves. We have integration tests that check that this does end up with
the correct reservation of quants, even if two order lines have different
owners. If we decide instead to propagate the owner_id field of the picking as
well, we will have to split pickings accordingly in case a sale order has lines
with different owners. See the discussion on
https://github.com/odoo/odoo/pull/4548 for details.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_owner_stock_sourcing%0Aversion:%2010.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>
* Cédric Pigeon <cedric.pigeon@acsone.eu>

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

