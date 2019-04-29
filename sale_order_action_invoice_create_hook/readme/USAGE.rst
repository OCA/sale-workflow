#. Add dependency of this module
#. Inherit from 'sale.order'
#. Change the _get_invoice_group_key function in order to return more
   grouping fields to take into account when creating a single invoice from
   various Sales Orders.
#. Change the _get_draft_invoices function in order to take into account
   existing draft invoices when creating new ones. This feature is already
   implemented in the module sale_merge_draft_invoice.
