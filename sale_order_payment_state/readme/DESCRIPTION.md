This module shows on sales orders whether their invoices are paid.

The standard *Invoice Status* tells how far an order is invoiced, not
whether the invoices are paid. This module adds:

- **Payment Status**: the payment status of the posted customer invoices
  and credit notes of the order: *No Invoice*, *Not Paid*, *Partially
  Paid*, *In Payment* or *Paid*. Draft invoices, and invoices that are
  fully reversed by a credit note, are ignored.
- **Amount Due**: the open amount of those invoices minus the open amount
  of the credit notes, in the order currency. Only visible to users with
  invoicing or accounting read access.

Both fields are stored, so they can be used to filter, group and sum
orders in the list view.

The Payment Status only covers what is invoiced. An order can be *Paid*
while its *Invoice Status* is still *To Invoice*: everything billed so far
is paid, but there is still something left to invoice.

The Payment Status is determined from the remaining invoices as follows:

1. no invoice left: *No Invoice*;
2. all paid: *Paid*;
3. all paid or in payment: *In Payment*;
4. none paid at all: *Not Paid*;
5. otherwise: *Partially Paid*.
