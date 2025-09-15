This module allows you to cancel the remaining quantity on sale order by adding
a dedicated action to sale lines. It also add two new fields to track canceled
and remaining to deliver quantities.

This module differs from the original odoo behavior in the following way:

* In odoo, if the update of the quantity ordered is allowed on the sale order at
  the confirmed state, odoo will recompute the required stock operations
  according to the new quantity. This change is possible
  even the stock operations are started for this sale order line.
* In this module, you can either decide if only the canceled quantity gets tracked
  or if it also should decrease the original ordered quantity.
