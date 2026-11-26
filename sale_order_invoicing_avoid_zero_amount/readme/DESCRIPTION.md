By default, a confirmed sale order with zero-amount lines that have quantities
pending to invoice is shown as *To Invoice*.

This module sets the invoice status of such orders to *Nothing to Invoice* when
every line pending to invoice has a zero total amount.

Orders with at least one line to invoice with a non-zero total (for example,
because of a fixed-amount tax) keep the *To Invoice* status, and the zero-amount
lines are still included in the invoice.
