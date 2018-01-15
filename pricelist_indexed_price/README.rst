.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

============================
Indexed prices on pricelists
============================

This module was written to extend the functionality of price lists to support indexed prices. This means that starting from some base price (the original product price), you can define date ranges where some factor is applied on the price. This is possible with standard Odoo, but a little bit inconvenient. This module saves you the manual work of creating all the price list items neccessary yourself.

Configuration
=============

To configure this module, you need to:

#. go to Accounting / Configuration / Price indexes
#. create an index, which is just a mapping from periods to price levels, by either creating ranges manually or using the wizard to generate periods
#. in a price list item, select computation method `Index` and select your price index
#. now if your price list item is picked according to the usual rules, the price will be adjusted from the index, that is the product's price multiplied by the current indexing factor

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/167/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Do not contact contributors directly about help with questions or problems concerning this addon, but use the `community mailing list <mailto:community@mail.odoo.com>`_ or the `appropriate specialized mailinglist <https://odoo-community.org/groups>`_ for help, and the bug tracker linked in `Bug Tracker`_ above for technical issues.

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
