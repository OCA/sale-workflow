Sale Amendment
==============

This module is meant to assist the users in handling the cases when a customer
changes his mind about a sale order. See also `purchase_amendment` (in
https://github.com/OCA/purchase-workflow), which will help cover similar cases
when you are using drop shipping, or for make to order products.


Background information
======================

This describes the problem the module solves. Feel free to skip
if you are only interested in the solution.

Common situations faced in real life by end users:

1. the Customer wants to decrease the quantity to be shipped for an ordered
   product.

   There is a remaining quantity to be shipped and the customer wants less than
   initial order (but he still wants some, so you can't blindly cancel the sale
   order)

   When asked, the supplier or the logistics department, they say OK.

   The end user is stuck with the system and can't do anything. The only way
   out: cancel the remaining deliveries, the sale order goes in exception,
   click "manually corrected", do the same for the purchase order if necessary,
   make a new sale order (and a new purchase order for MTO / drop
   shipment). That's not really good but it works.

   However, this does not work with an order for 1000 products, and of which
   200 were already shipped the customer wants only to receive 600 instead of
   the remaining 800: it is not possible to split a picking in order to cancel
   the proper quantity. Canceled sale order line do not cancel their linked
   delivery and even worse: if you cancel a sale order line on a draft sale
   order, and then confirm the order, the line gets to confirmed...

2. the Customer wants to increase the quantity to be shipped of an ordered
   product.

   There is a remaining quantity to be shipped and the customer wants more of the
   product.

   When asked, the supplier or the logistics department, they say OK.

   The end user is blocked with the system and can't do anything. The only way out:
   make a new sale order (and purchase order for MTO / drop shipment). That's
   not really good but it works.

3. the Customer wants to cancel the remaining quantity of a product

   There is a remaining quantity to be shipped and the customer wants to cancel
   it. The only way to go is to is to cancel all remaining, and regenerate (and
   if there are other lines to be shipped, the same issue than in point 4 are
   there...)

   * When asked, the supplier or the logistics department, they say OK.
   * Cancel the remaining picking
   * the sale order goes in exception, user clicks "manually corrected"
   * Same for purchase order

   Problems with this solution: the historical values are lost. They can be
   logged in the chatter, but this is not ideal.

4. the Customer wants to cancel a whole line of a product, not yet shipped

   On the sale order, some lines have already been shipped, there are still
   some lines to ship.

   When asked, the supplier or the logistics department, they say OK.

   The end user is stuck with the system and can't do anything. It is not
   possible to split a delivery so it is not possible to  can cancel the proper
   line. The only work around: make note in the chatter. Once only the line to
   be cancelled is the only remaining line to be delivered, it is possible to
   cancel it like in point 3 above.

5. the Customer wants to cancel a sale order, no yet shipped

   This one works:

   * When asked, the supplier or the logistics department, they say OK.
   * Cancel the pickings of the sale order
   * Cancel the purchase order
   * Cancel the sale order

6. the Customer wants to add a new product in an existing confirmed sale order

   Create a new sale order :)


Conclusion

* `5.` and `6.` are ok
* `1.` and `2.` are ok, but tedious
* `3.` is tedious if there are no other products, but otherwise, it's like `4.`...
* `4.` it may work, but is really error prone

The solution proposed by Sale Amendment / Purchase Amendment does not bypass
any of the system process, but provides some automation so that the process
does not take too much time and is less error prone.


Usage
=====

If you allow to use the process made available by this addon, we advise that
the invoice policy is 'based on delivery'. The module will not allow amending
an invoiced sale order, to prevent the invoicing to be wrongly made or too much
time consuming at every change happening in the logistics chain.

This module respects the best practices in term of segregation of
responsibilities and does not bypass any workflow. It just here to ease the
user experience and have a way to have a final sale order with the proper
information (how much has been canceled, how much has been shipped). With the
standard, you only have this information in the pickings.

When one of the cases described above is encountered, the process to handle 
starts with the related picking. A wizard is available to split the picking
lines (stock moves), and it handles the proper reconnection of the logistic
flows in case of chained moves. 

Let's take an example from case 1: there was an initial order of 50 units and
the customer says he wants only 35, you split the picking to get two lines, one
with 35 units and the other one with 15 units. The line with 15 units can be
canceled. This causes the sale order to go in shipping exception. 

In that state, this addon adds a button labeled 'Amend' which displays a
wizard, with a summary of the sale order  lines, showing for each product the
quantity ordered, the quantity delivered, the quantity canceled. The user can
edit the quantity to ship (to a value up to ordered - delivered). When
validated, the wizard will:

* split / cancel the sale order lines according to the values specified
* if necessary, recreate a procurement for the quantity to be delivered based
  on the updated quantity to be delivered
* record the reason given for the amendment in the chatter

In the sale order form view, the canceled lines are in grey, and the various
quantities are displayed in the sale order lines. The total amount of the sale 
order is now computed ignoring the canceled lines.

Known issues / Roadmap
======================

version 2.0
-----------

* the SO report display the state of a SO line so we can re-send the order to
  the customer to show him the new status of his order.



version 3.0
-----------

* Add version number on SO
* When I amend a SO, before splitting line of original SO, a new copy is made,
  but we continue to work with the original one (the copy is the archived
  version):

   - The original SO number is now SO number + ‘-’ + Version
   - The archived version is canceled and inactivated (to avoid having it in the list of SO)

* Add tab “Amendment” O2M containing datetime, user, reason, SO version
  (archived version)
  
* Based on : https://github.com/OCA/sale-workflow/compare/7.0...akretion:70-add-sale_order_revision and 
 https://github.com/OCA/purchase-workflow/tree/7.0/purchase_order_revision

Credits
=======

Contributors
------------

* Joel Grand-Guillaume <joel.grandguillaume@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Guewen Baconnier <guewen.baconnier@camptocamp.com>

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
