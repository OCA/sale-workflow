This module adds a **Sale Contact** field to quotations, sale orders, and invoices.

**Key concept — keep the company as customer, name the person who drives the deal**

In standard Odoo, ``partner_id`` is the commercial/legal counterpart of the
document: it drives the fiscal position, pricelist, payment terms, receivable
account and the invoice/shipping addresses. While it *can* technically hold a
child contact, using it to store the "contact person" forces an individual into
a field that is meant to represent the invoiced/contracted entity — polluting
analytic accounting and reporting.

This module addresses a *different need*: tracking a named **commercial contact
person** (e.g. procurement manager, project lead, key account contact) who is
the day-to-day point of contact for a deal, **while keeping the company as the
commercial entity** in ``partner_id``. That person travels consistently across
the sale order, its invoices, and (with the companion module) any generated
projects — something ``partner_id`` cannot guarantee, since each document
computes its own ``partner_id``.

Billing and shipping addresses remain independent and unaffected.

This distinction is also fully **compatible with B2C**: when the customer is
an individual without child contacts, the field simply remains empty and the
ordinary Odoo workflow is unchanged.

The sale contact field allows you to:

* Select a specific contact person for a sale order or quotation
* Automatically propagate the contact from sale order to generated invoices
* Display the contact person on PDF reports (quotations, orders, invoices)

The contact must be a child contact (person) of the selected customer.
