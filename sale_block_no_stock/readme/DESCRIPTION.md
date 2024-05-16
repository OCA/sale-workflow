This module extends the functionality of Sales to support blocking sales and to allow you to ensure you are capable to send product you have in stock.

When a Sale Order is going to be confirmed, it will be checked if the quantity demanded exceeds that of the field selected in the configuration, and in this case a wizard will appear to allow you to fix quantities indicating what is the maximum quantity that can be ordered.

Then, you can adjust UoM quantities, Packaging quantities or move remaining unfixed lines to a new order.

If the user who is confirming an order has a group that is allowed, an extra option to confirm the Order with errors will appear on the Wizard.

This module only can block lines with product type 'product' (storable products).
