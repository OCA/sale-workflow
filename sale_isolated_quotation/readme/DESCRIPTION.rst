In some countries/companies, it is already common to separate these two documents.
For filing purposes, the document sequence of quotation and sales order
has to be separated. In practice, there could be multiple quotations open
to a customer, yet only one quotation get converted to the sales order.

This module separate quotation and sales order by adding order_sequence flag in
sale.order model.

Each type of document will have separated sequence numbering.
Quotation will have only 2 state, Draft and Done. Sales Order work as normal.
