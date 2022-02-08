This odoo module adds a field on Sales Order indicating whether it has been fully invoiced, partially invoiced, if only the downpayment has been invoiced or if it has not been invoiced at all.

This is different from the built-in "Invoice Status" field in Odoo:
Invoice Status only indicates if there is something ready to invoice; this module, like sale_delivery_state, shows if the Sales Order has been invoiced or not. The difference is particularly relevant, for example, when only part of a Sales Order has been delivered and invoiced. Invoice Status will show that there is nothing more to invoice at the moment, while the "Invoiced" field this module introduces shows that the order has been partially invoiced so far.
