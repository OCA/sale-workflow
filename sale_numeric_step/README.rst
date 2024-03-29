=========================
Sale numeric step widgets
=========================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:9bcbd2bb27868696c206e9a2d296ff57c53bac747aa0a2731f9b90f307701e17
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Alpha-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Alpha
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fsale--workflow-lightgray.png?logo=github
    :target: https://github.com/OCA/sale-workflow/tree/16.0/sale_numeric_step
    :alt: OCA/sale-workflow
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/sale-workflow-16-0/sale-workflow-16-0-sale_numeric_step
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/sale-workflow&target_branch=16.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module adds (-) and (+) buttons to some numeric inputs of sales
orders.

.. IMPORTANT::
   This is an alpha version, the data model and design can change at any time without warning.
   Only for development or testing purpose, do not use in production.
   `More details on development status <https://odoo-community.org/page/development-status>`_

**Table of contents**

.. contents::
   :local:

Use Cases / Context
===================

This module was developed because salespersons usually use touch devices
on the field, and having +/- buttons in those devices helps them fill
sale orders more quickly.

Usage
=====

To use this module, you need to:

1. Open or create a sales order.
2. Use the new input capabilities in qty and price fields.

Those capabilities come from the ``web_widget_numeric_step`` module.
Check `its
documentation <https://odoo-community.org/shop/web-widget-numeric-step-5231>`__
for more details.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/sale-workflow/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/sale-workflow/issues/new?body=module:%20sale_numeric_step%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* Moduon

Contributors
------------

-  Jairo Llopis (`Moduon <https://www.moduon.team/>`__)

Other credits
-------------

The development of this module has been financially supported by:

-  Moduon Team S.L.

Maintainers
-----------

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

.. |maintainer-rafaelbn| image:: https://github.com/rafaelbn.png?size=40px
    :target: https://github.com/rafaelbn
    :alt: rafaelbn
.. |maintainer-yajo| image:: https://github.com/yajo.png?size=40px
    :target: https://github.com/yajo
    :alt: yajo

Current `maintainers <https://odoo-community.org/page/maintainer-role>`__:

|maintainer-rafaelbn| |maintainer-yajo| 

This module is part of the `OCA/sale-workflow <https://github.com/OCA/sale-workflow/tree/16.0/sale_numeric_step>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
