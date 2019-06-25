Odoo can merge sales orders into a single invoice, grouped by partner and
currency, when the sales orders are selected and invoiced together. This module
extends the grouping to also consider any pre-existing draft invoices and merge
them.

This feature is activated from Sales / Settings and assigned to the company
settings.

Users assigned to the group 'Change sale to invoice merge proposal'
have the possibility to activate or deactivate this option at the moment of
invoicing.

If you also need to group on fields other than partner and currency, the OCA
module sale_invoice_group_method allows you to specify alternative grouping
methods and is fully compatible with this module.
