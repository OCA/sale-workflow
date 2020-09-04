.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=====================
Sale quotation number
=====================

* Sale Quotation:
    * Sale process in draft stage just informing prices and element of communication.

* Sale Order:
    * Sale process confirmed, the customer already have a compromise with us in terms of pay an invoice and receive our product or service.

Originally Odoo manage only 1 sequence for this 2 documents, then the sales order won and lost manage the same sequence losing
almost all lost quotations in terms of sequences, making so difficult understand with a quick view if we are good or bad in terms of
logistic and sale process already confirmed.


**Technical Explanation**

When you create a quotation, it is numbered using the 'sale.quotation'
sequence.  When you confirm a quotation, its orginal number is saved in the
'origin' field and the sale order gets a new number, retrieving it from
'sale.order' sequence.

* With Odoo Base:

    Sale Quotation 1 Number = SO001

    Sale Quotation 2 Number = SO002

    Sale Quotation 3 Number = SO003

    Sale Quotation 4 Number = SO004

* With Odoo + This Module:

    Sale Quotation 1 Number = SQ001

    Sale Quotation 2 Number = SQ002

    Sale Quotation 3 Number = SQ003

    Sale Quotation 4 Number = SQ004

    Sale Quotation 2 Confirmed = Number for Sale Order SO001 from Sale Quotation SQ002

    Sale Quotation 1 Confirmed = Number for Sale Order SO002 from Sale Quotation SQ001

    Sale Quotation 4 Confirmed = Number for Sale Order SO003 from Sale Quotation SQ004

Configuration
=============

To configure this module you need to go to Sales -> Configuration and uncheck 'Use same enumeration for quotations and sale orders'.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/11.0

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

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Andy Lu <andy.lu@elico-corp.com>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Valentin Vinagre Urteaga <valentin.vinagre@qubiq.es>
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>

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
