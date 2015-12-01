Sale Quotation Sourcing
=======================

Description
===========

This module implements manual sourcing of sale order lines from purchase
order lines.

Instead of having the confirmation of a SO generate procurements which in
turn may generate a PO, we invert the process: in order to generate a quote
for a customer, we ask quotes to different suppliers.

Once the sale quotation is accepted by the customer and the user confirms
it, a wizard is presented to choose which PO to use to source the SO lines.

The process should mimic closely the way that Odoo handles a MTO, buy
order. The only difference is that the PO is chosen manually and not
automatically generated. The end result should be the same.

To show that, two test cases are provided that show the standard process
and the manually sourced one.

The drop shipping case is handled as well, with a warning to check if the
destination locations of the procurement and the sourced PO are consistent.
In addition to that, when the user sources a sale line with a purchase
line, the system tries to choose automatically an appropriate route (MTO or
drophipping).

This on_change method is the only place where the module stock_dropshipping
is used, otherwise it contains little more than preconfigured Routes,
Rules, and Picking Types. All other code and the tests do not use it.  That
dependency can be easily removed later if it is needed to manually
configure dropshipping and MTO routes.

Note: the package nose is required to run the tests. It is not noted in the
external dependencies since it is not required in production.



Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_quotation_sourcing%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>
* Joël Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Nicolas Bessi <nicolas.bessi@camptocamp.com>

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
