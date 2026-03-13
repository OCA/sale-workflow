Adds a button "Paid" on a sent sales order.

The action will confirm the SO and, in case of website order, it will also mark
as done the pending payment transaction. For manually created order, a payment
transaction will be created.
Note that marking as done the payment transaction will change the invoicing
policy to on order (odoo standard). This can also enable standard automatic
invoicing.

This is especially convenient for wire transfer, to mark the SO as paid.
It can also serve for other payment mode in case the postprocessing failed but
the payment went through.
