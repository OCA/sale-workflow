This module makes the availability icon shown next to the quantity on a sales
order line take into account the stock available on **every warehouse**, not
only the warehouse assigned to the sales order line.

The widget icon next to the quantity is colored as follows:

- **Blue/purple** (the original color): there are enough stock on the line's own
  warehouse to fulfill the demand.
- **Yellow**: the line's own warehouse can not fulfill the demand on its own, but
  the demand can be satisfied by gathering the stock of all the warehouses.
- **Red**: there is not enough stock to fulfill the demand even when gathering the
  stock of all the warehouses.

Clicking on the icon opens the availability popover, which now also shows a
breakdown of the available quantity on each warehouse.
