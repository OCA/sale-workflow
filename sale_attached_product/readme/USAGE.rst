Now that you have your product configured:

#. Place a new sale order and then add that product in a new line.
#. Once you save your order, the attached products will be added in new lines to the
   order with as many quantities as the main one.

If the global `sale_attached_product.auto_update_attached_lines` setting is on:

#. Update the main product quantity and the attached product quantities will be updated
   in the same amount as well.
#. If we delete the main line, the attached ones will go away in any case.
