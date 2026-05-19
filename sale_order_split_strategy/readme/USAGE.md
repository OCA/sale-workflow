To use this module you first need to create splitting strategies to apply on sales order.

    Sales -> Configuration -> Split Strategies

The splitting is based on an ir.filter applied on sale.order.line.

Then on sales order, the Split Strategy field allows to select the corresponding strategy.
After which a button `Split` is available on the form to split an order.

If the field "Force split" on the SO is checked, the split will occur automatically on order confirmation. All orders (the original and the split ones) will be confirmed all at once
