This module lets you define, on a customer, a separate partner that is in
charge of receiving and paying its invoices.

Unlike a standard *Invoice Address* (a child contact of the same company),
the **Invoice To** partner can be a completely independent customer. When a
sales order is created for the customer, its *Invoice Address*
(`partner_invoice_id`) is set to the **Invoice To** partner, so the invoices
generated from the order are owed by that partner instead of by the ordering
customer.
