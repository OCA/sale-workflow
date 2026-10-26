- Standard Odoo can already invoice several sale orders together (*Create
  Invoices* with consolidated billing), but cannot produce a single order
  document out of them. This module does.
- The implementation follows `purchase.order.action_merge()` of the Purchase
  application: a server action bound to the list view, no wizard.
- We did not migrate the [existing module on v8.0](https://github.com/OCA/sale-workflow/tree/8.0/sale_order_merge) nor the [existing PR to v17.0](https://github.com/OCA/sale-workflow/pull/3904), because it was too complex and outdated (merging other states, involving pickings and invoices). Instead we implemented a similar approach as today's Odoo standard does on the Purchase Order side.
