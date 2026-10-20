1. Create a sale order.
2. Add a line with a product: its warehouse defaults to the sale order one,
   but you can change it.
3. Add a second line with a product:
   - if both lines use the same warehouse, different from the sale order one,
     the sale order warehouse is changed to it on confirmation;
   - if the lines use different warehouses, an advice message is displayed.
