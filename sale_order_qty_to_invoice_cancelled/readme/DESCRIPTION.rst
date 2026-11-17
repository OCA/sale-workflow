This module sets the sale order quantity to invoice to the quantity invoiced 
when the sale order is cancelled on lines with order as invoice_policy.

This allows to generate a credit note for the order by simply calling
create_invoice(final=True) on the sale order.
