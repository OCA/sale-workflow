When a sale order is created for a customer having a *Sale Priority*, the
order gets that priority, and `sale_order_priority` propagates it to the
order lines.

It is only applied on creation: it is never reapplied afterwards, so you are
free to change the priority of an existing order, and changing the customer
of an existing order leaves its priority untouched.
