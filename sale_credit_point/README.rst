.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Sale Credit Point
=================

Sale based on partners' credit point.

Use case
--------

You have employees that have some credit (up to you where this come from)
and you allow employees to buy products based on this credit.

Products are sold by points rather than money.


Features and usage
------------------

Partner model has a new field `credit_point` which can be updated easily
via a smart button on the partner form.

A new currency is created `PT` (points) and is used by default
for `credit_point` field.

On order confirmation the amount of the order
is compared with partner's credit:

   a. credit is not enough on partner -> the order cannot be confirmed
   b. no credit is left on partner
      but the user is member of `Manage credit point` -> order can be confirmed
   c. no credit is left on partner
      but the context has key `skip_credit_check` -> order can be confirmed

If the order is confirmed the credit is deducted from partner.


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

* Simone Orsi <simone.orsi@camptocamp.com>

Do not contact contributors directly about support or help with technical issues.


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
