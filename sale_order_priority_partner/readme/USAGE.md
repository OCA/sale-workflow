When a customer having a *Sale Priority* is selected on a quotation, the order
gets that priority, and `sale_order_priority` propagates it to the order lines.
It is only a default: an explicit priority passed at creation time is
kept, and you are free to change the priority of an order afterwards.

If the customer has no *Sale Priority* of its own, the one of its
commercial entity is used.

If the partner is changed on an existing order, the priority is updated by an
onchange.
