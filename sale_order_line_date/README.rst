.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Sale order line date
====================

This module adds commitment date to a sales order lines and propagate it to
stock moves and procurements.
When the commitment date of the whole sale order is modified the commitment date
of the lines change to match.

Usage
=====

Create a Quotation or a Sales Order and it fills the commitment date in the sale
order line

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/167/11.0

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
* Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>
* Esther Martín <esthermartin@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Ana Juaristi <anajuaristi@avanzosc.es>
* Jordi Ballester <jordi.ballester@eficent.com>
* Aaron Henriquez <ahenriquez@eficent.com>
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>
* Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
* Open-Net Sàrl <jae@open-net.ch>

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
