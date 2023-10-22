This module provides different configuration option to manage packagings on
sale orders.

The creation/update of sale order line will be blocked (by constraints) if the data on the
sale.order.line does not fit with the configuration of the product's packagings.

It's also possible to force the quantity to sell during creation/modification of the sale order line
if the "Force sale quantity" is ticked on the packaging and the "Sell only by packaging" is ticked on product.

For example, if your packaging is set to sell by 5 units and the employee fill
the quantity with 3, the quantity will be automatically replaced by 5 (it always rounds up).
