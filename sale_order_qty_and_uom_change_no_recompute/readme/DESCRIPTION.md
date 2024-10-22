This module is based on the module sale_order_qty_change_no_recompute
and adapts it to also make the unit of measure not taken into account
in the price unit recompute.

A lot of business don't set different prices according the quantity of
the product to sell, and they see very annoying to set a manual price
after the negotiation with the customer, and see it changed when they
vary the demanded quantity.

This module prevents this avoiding the recomputation of the price unit,
discount and pricelist item fields if only the quantity has been changed
in the sales order line.

Some business also do not want the lines to be recomputed when they 
change the unit of measure. This module also prevents that.
