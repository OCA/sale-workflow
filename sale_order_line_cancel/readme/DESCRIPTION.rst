This module allows you to cancel the remaining quantity on sale order by adding
a dedicated action to sale lines. It also add two new fields to track canceled
and remaining to deliver quantities.

This module differs from the original odoo behavior in the following way:

* In odoo, if the update of the quantity ordered is allowed on the sale order at
  the confirmed state, odoo will recompute the required stock operations
  according to the new quantity. This change is possible
  even the stock operations are started for this sale order line.
* In this module, the quantity ordered is not updated on the sale order line to
  keep track of the original ordered by the customer. At the same time, we
  cancel only the stock moves for the remaining qty to deliver. This is only
  possible if no operation is started for this sale order line.


.. warning::

    It's not recommended to use this module if the update of the quantity ordered
    on the sale order line is allowed the confirmed state. This could lead to
    unpredictable behavior.
