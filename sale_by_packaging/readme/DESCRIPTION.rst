This module provides different configuration option to manage packagings on
sale orders.

By default there is a Warning message during the modification/creation of a sale order line
to notice the user when the quantity to sell doesn't fit with the factor set on the packaging.

It's also possible to force the quantity to sell during creation/modification of the sale order line
if the "Force sale quantity" is ticked on the packaging.

For example, if your packaging is set to sell by 5 units and the employee fill
the quantity with 3, the quantity will be automatically replaced by 5 (it always rounds up).
