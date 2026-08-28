This module provides different configuration option to manage packagings
on sale orders.

Since Odoo 19.0, packagings are units of measure: the additional units set
on a product (field "Packagings") are the units it can be sold by, on top
of its own unit.

The creation/update of sale order line will be blocked (by constraints) if
the data on the sale.order.line does not fit with the configuration of the
product's packaging units.

It's also possible to force the quantity to sell during
creation/modification of the sale order line if the "Force sale quantity"
is ticked on the packaging unit and the "Sell only by packaging" is ticked
on product.

For example, if your packaging unit is a box of 5 units and the employee
fills the quantity with 0.6 box, the quantity will be automatically
replaced by 1 box, so 5 units (it always rounds up).
