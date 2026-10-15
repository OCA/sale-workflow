Adds a button "Paid" on a sent sales order. This is especially convenient for
wire transfer, to mark the SO as paid. It can also serve for other payment
modes in case the postprocessing failed but the payment went through.

The action will confirm the SO. An email confirmation will be generated to
notify the client that the order has been confirmed.

When there is pending payment transaction (for instance for webshop orders),
the transaction will be confirmed.

The SO invoicing policy will be forced to on order to be able to generated the
invoice for any non invoiced line.

According to odoo standard settings, the invoice will be posted and the invoice
will be sent.
