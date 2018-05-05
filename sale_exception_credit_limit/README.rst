.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========================
Sale Exception Credit Limit
===========================

#. It adds a new group 'can modify credit limit', only users with this group are allowed to change credit limit on partners.
#. It also adds an exception to check that you can not aproove sale orders that would exceed credit limit. It checks:

* The current due of the partner
* The amount of Sale Orders aproved but not yet invoiced
* The invoices in draft state.
* The amount of the Sale Order to be aproved and compares it with the credit limit of the partner. If the credit limit is below this, then it is not to approve the Sale Order.


Installation
============

To install this module, you need to:

#. Only need to install the module


Configuration
=============

To configure this module, you need to:

#. Set 'can modify credit limit'=true or false, on user profile preferences.


Usage
=====

To use this module, you need to:

#. When you confirm a sale order, validate than the partner limit not overdo

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: http://runbot.adhoc.com.ar/

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/sale/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* |company| |icon|

Contributors
------------

Maintainer
----------

|company_logo|

This module is maintained by the |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
