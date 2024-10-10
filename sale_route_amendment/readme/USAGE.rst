..warning::

  When you change the route on a sale order line, the related move will
  be cancelled. If your warehouse is configured with a multi steps route
  for the delivery (for example: pick -> pack -> ship), the cancellation
  of the initial move (ship) will not be enough to cancel the whole chain.
  You will have to configure the stock rules of the delivery route to propagate
  the cancellation of the move.


To tests this addon, you can follow the steps below:

1. Install the addon on your database.
2. Create a sale order with a product managed in stock.
3. Confirm the sale order.
   -> The sale order will be confirmed and the stock move will be created for the initial route.
4. Edit the sale order and change the route to a new route.
   -> The initial move will be cancelled and a new move will be created for the new route.
