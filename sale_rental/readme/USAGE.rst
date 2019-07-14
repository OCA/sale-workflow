In a sale order line (form view, not tree view), if you select a rental service, you can :

* create a new rental with a start date and an end date: when the sale order is confirmed, it will generate a delivery order and an incoming shipment.
* extend an existing rental: the incoming shipment will be postponed to the end date of the extension.

In a sale order line, if you select a product that has a corresponding rental service, you can decide to sell the rented product that the customer already has. If the sale order is confirmed, the incoming shipment will be cancelled and a new delivery order will be created with a stock move from *Rental Out* to *Customers*.
