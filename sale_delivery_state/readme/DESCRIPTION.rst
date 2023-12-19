This odoo module add delivery state on the sale order.

Delivery state is computed based on `qty_delivered` field on sale order lines.

This is usefull for other modules to provide the state of delivery.
The state of the sale order can be forced to fully delivered in case
some quantities were cancelled by the customer and you consider you have
nothing more to deliver.

Sale order lines can have products or services, as long as the field `qty_delivered`
is set, it will trigger the computation of delivery state.

Sale order lines with the Skip Delivery State field set to True will be ignored when
computing the delivery state. This field is automatically set depending on the field
Sales > Configuration > Quotations & Orders > Skip Service products for Sale Delivery
State. If set to True, the field Skip Delivery State in sale order lines containing
service products will be automatically set to True, but it can manually changed.

This module also works with delivery.carrier fees that are added as a
sale order line. Thoses line are special as they will never be considered delivered.
Delivery fees lines are ignored in the computation of the delivery state.
