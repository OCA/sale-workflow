.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Sale Order Multiple Discount
============================

Often the total discount on a sale order line is the result of multiple cumulative discounts offered
to the customer for different reasons. Sometimes, it's desirable to display a detail of how the total
discount on a SO line was computed.

This module allows to express discounts on SO lines as mathematical expressions rather than a single number.
For example, if I wish to offer to a particular customer a 10% discount for the selected payment method and
an additional 20% discount for the selected payment term, on Odoo I should write a total discount of 28%;
Using this module, instead, I can simply write '10+20' in the discount column.

This module implements this feature also on invoices, and takes care of propagating a discount expression from
a sale order to its destination invoice(s).

Usage
=====

To use this module, you need to enable the group 'Discount on lines' on the target user

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/sale-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Antonio Esposito <a.esposito@onestein.nl>

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
