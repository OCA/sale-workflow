This odoo module add delivery state on the sale order line. It is based on the
module sale_delivery_state, which adds the field at sale order level.

Delivery state is computed based on `qty_delivered` field on sale order line.

The state of the sale order line can be forced to fully delivered in case
some quantities were cancelled by the customer and you consider you have
nothing more to deliver.

Sale order lines can have products or services, as long as the field `qty_delivered`
is set, it will trigger the computation of delivery state.

This module also works with delivery.carrier fees that are added as a
sale order line. Thoses line are special as they will never be considered delivered.
Delivery fees lines are ignored in the computation of the delivery state.
