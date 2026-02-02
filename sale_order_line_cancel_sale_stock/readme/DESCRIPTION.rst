This module cancels only the stock moves for the remaining qty to deliver.
Also it will track the canceled qty if a order line's stock move is canceled
but only if there are not other started operations for this sale order line.

When the base addon is configured to also decrease the original ordered qty
it ensures that there are now new moves created. Because by default,
odoo will recompute the required stock operations if the ordered qty is changed.
By canceling the operations for the remaining qty before the ordered qty is changed,
odoo will not recompute the required stock operations, because the qty done by moves
is the same as the ordered qty.


.. warning::

    It's not recommended to use this module if the update of the quantity ordered
    on the sale order line is allowed the confirmed state. This could lead to
    unpredictable behavior.
