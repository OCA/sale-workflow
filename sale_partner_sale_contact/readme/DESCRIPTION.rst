This module adds a **Sale Contact** field to quotations, sale orders, and invoices.

**Key concept — not another address field**

Odoo already supports invoice and delivery addresses on partners, and the sale
order form exposes those as distinct fields. This module addresses a *different
need*: tracking a named **commercial contact person** (e.g. procurement
manager, project lead, key account contact) who is the day-to-day point of
contact for a deal. That person travels consistently across the sale order, its
invoices, and (with the companion module) any generated projects — while the
billing and shipping addresses remain independent and unaffected.

This distinction is also fully **compatible with B2C**: when the customer is
an individual without child contacts, the field simply remains empty and the
ordinary Odoo workflow is unchanged.

The sale contact field allows you to:

* Select a specific contact person for a sale order or quotation
* Automatically propagate the contact from sale order to generated invoices
* Display the contact person on PDF reports (quotations, orders, invoices)

The contact must be a child contact (person) of the selected customer.
