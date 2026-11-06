Business Need
In many manufacturing workflows, products are sold to customers via Sales Orders and subsequently manufactured through Manufacturing Orders (MOs). Often, these manufactured products require various components that are consumed during production and tracked via Bills of Materials (BoMs).

However, in certain business scenarios, it's necessary not only to manufacture a finished product but also to invoice the customer for the individual components used in production, especially when the components themselves are valuable, consumable, or customer-specific.


Odoo, by default, does not automatically add consumed components to the related Sale Order. This leads to:

- Manual effort in identifying and adding consumed items for invoicing.
- Risk of underbilling customers for actual material usage.
- Inconsistencies between manufacturing records and customer billing.

Module Purpose
This module addresses the above gap by automatically adding all `sale_ok=True` components that were actually consumed in a Manufacturing Order to the linked Sale Order. It ensures:

- Full traceability and billing accuracy of component usage.
- Avoidance of double entry by manufacturing and sales teams.

Compatibility with multiple MOs linked to the same SO (incrementing quantities when the same component is used more than once).

Real word use case:
This module is very usefull in a subcontractee scenario.
E.g. the customer is the owner of the component and endproduct.
But the subcontractee is providing operations over the product and adding components.
These components need to be invoiced separately to the customer.
In this scenario, the raw material supplied by the customer is not saleble.
(He already owns it and gives it in consinee to the subcontractee.)
The added components should be set up as salebale products.

With this module installed and the scenario where consumption of the components are added to a mo.
Upon "mark done" of the MO the consumed components are added to the sale order.
Making them invoicable to the customer.
