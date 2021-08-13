Computes the sales order `expected_date` and delivery order `scheduled_date`
with respect to the warehouse calendar

This module is incompatible with `sale_partner_delivery_window`,
since there's no proper way to manage the execution order of
`sale.order.line._expected_date()` and `sale.order.line._prepare_procurement_values()`.
