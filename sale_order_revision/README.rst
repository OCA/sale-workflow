Sale Order Revision
===================

This module allows to revise sale_orders that are not in a state
accepted/ordered/finished/draft.

The revision is done using a Review button added in the header of sale order.
In addition, two new links have been added: *Revised by* and *Revision of*. The
links ease to follow the historic of the revisions.

The revised sale order is set to *cancel* state. It has been done this way to
keep standard workflow.

To detect a sale order as a revised sale order, it is adviced to filter:
 * sale orders at *cancel* state
 * and *Revised by* is not empty


Original Sale Order:

.. image:: /sale_order_revision/static/img/1_original_sale_order.png


New Sale Order:

.. image:: /sale_order_revision/static/img/2_new_sale_order.png


Revised Sale Order

.. image:: /sale_order_revision/static/img/3_revised_sale_order.png

Installation
============

No installation steps required other than installing the module itself.

Configuration
=============

No configuration required.

Usage
=====

* Click the new button to revise a sale order
The button appears only to member to group Sale Reviser and depending on its status.

* When a user revises a sale order:

 - the revised sale.order is duplicated
 - the new sale order has a link to the original sale order
 - the revised sale order is set to cancel status
 - the revised sale order has a link to the new sale order


Credits
=======

Contributors
------------

* Jordi Riera <jordi.riera@savoirfairelinux.com>
* William BEVERLY <william.beverly@savoirfairelinux.com>
* Bruno JOLIVEAU <bruno.joliveau@savoirfairelinux.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

More information
----------------

Module developed and tested with Odoo version 8.0.

For questions, please contact our support services
<support@savoirfairelinux.com>
