This module bridges *Sale Readonly* and *Stock Readonly*: it grants
users holding the stock read-only group access to the *Delivery* smart
button of sales orders.

Without this module, the button (added by the `sale_stock` standard
module) is reserved for stock users, so read-only sales users cannot
browse the deliveries of a sales order from its form view.

The module is auto-installed when *Sale Readonly*, *Stock Readonly* and
*Sale Stock* are installed.
