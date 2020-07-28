[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/167/9.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-sale-workflow-167)
[![Build Status](https://travis-ci.org/OCA/sale-workflow.svg?branch=9.0)](https://travis-ci.org/OCA/sale-workflow)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/9.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)

Odoo Sales, Workflow and Organization
======================================

This project aim to deal with modules related to manage sale and their related workflow. You'll find modules that:

 - Allow to group discounts / advances / fees separately
 - Add a condition on sales that is pushed on related invoices
 - Compute shipped rate differently
 - Easy the cancellation of SO
 - ...

[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[sale_automatic_workflow](sale_automatic_workflow/) | 9.0.1.1.1 | Sale Automatic Workflow
[sale_automatic_workflow_payment_mode](sale_automatic_workflow_payment_mode/) | 9.0.2.0.0 | Sale Automatic Workflow - Payment Mode
[sale_cancel_reason](sale_cancel_reason/) | 9.0.1.0.0 | Sale Cancel Reason
[sale_delivery_block](sale_delivery_block/) | 9.0.1.0.0 | Allow you to block the creation of deliveries from a sale order.
[sale_delivery_block_proc_group_by_line](sale_delivery_block_proc_group_by_line/) | 9.0.1.0.0 | Module that allows module sale_delivery_block to work with sale_procurement_group_by_line
[sale_double_validation](sale_double_validation/) | 9.0.1.0.0 | Double validation for Sales
[sale_exception](sale_exception/) | 9.0.1.1.0 | Custom exceptions on sale order
[sale_fixed_discount](sale_fixed_discount/) | 9.0.1.0.0 | Allows to apply fixed amount discounts in sales orders.
[sale_force_invoiced](sale_force_invoiced/) | 9.0.1.0.0 | Allows to force the invoice status of the sales order to Invoiced
[sale_open_qty](sale_open_qty/) | 9.0.1.0.1 | Allows to identify the sale orders that have quantities pending to invoice or to deliver.
[sale_order_digitized_signature](sale_order_digitized_signature/) | 9.0.1.0.0 | Sale Order Digitized Signature
[sale_order_line_date](sale_order_line_date/) | 9.0.1.0.0 | Sale Order Line Date
[sale_order_line_sequence](sale_order_line_sequence/) | 9.0.1.0.0 | Propagates SO line sequence to invoices and stock picking.
[sale_order_lot_selection](sale_order_lot_selection/) | 9.0.1.0.0 | Sale Order Lot Selection
[sale_order_price_recalculation](sale_order_price_recalculation/) | 9.0.1.0.0 | Price recalculation in sales orders
[sale_order_product_recommendation](sale_order_product_recommendation/) | 9.0.1.0.0 | Recommend products to sell to customer based on history
[sale_order_type](sale_order_type/) | 9.0.1.2.0 | Sale Order Types
[sale_order_variant_mgmt](sale_order_variant_mgmt/) | 9.0.1.0.0 | Handle the addition/removal of multiple variants from product template into the sales order
[sale_packaging_price](sale_packaging_price/) | 9.0.1.0.0 | Sale Packaging Price
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 9.0.1.0.0 | Base module for multiple procurement group by Sale order
[sale_procurement_group_by_requested_date](sale_procurement_group_by_requested_date/) | 9.0.1.0.0 | Groups pickings based on requested date of order line
[sale_product_set](sale_product_set/) | 9.0.1.0.1 | Sale product set
[sale_rental](sale_rental/) | 9.0.1.0.0 | Manage Rental of Products
[sale_revert_done](sale_revert_done/) | 9.0.1.0.0 | This module extends the functionality of sales to allow you to set a sales order done back to state 'Sale Order'.
[sale_sourced_by_line](sale_sourced_by_line/) | 9.0.1.0.0 | Multiple warehouse source locations for Sale order
[sale_start_end_dates](sale_start_end_dates/) | 9.0.1.0.0 | Adds start date and end date on sale order lines
[sale_validity](sale_validity/) | 9.0.1.0.0 | Set a default validity delay on quotations


Unported addons
---------------
addon | version | summary
--- | --- | ---
[account_invoice_reorder_lines](account_invoice_reorder_lines/) | 0.1 (unported) | Invoice lines with sequence number
[mail_quotation](mail_quotation/) | 0.1 (unported) | Mail quotation
[partner_prepayment](partner_prepayment/) | 8.0.1.0.0 (unported) | Option on partner to set prepayment policy
[partner_prospect](partner_prospect/) | 8.0.1.0.0 (unported) | Partner Prospect
[pricelist_share_companies](pricelist_share_companies/) | 1.0 (unported) | Share pricelist between compagnies, not product
[product_customer_code_sale](product_customer_code_sale/) | 1.0 (unported) | Product Customer code on sale
[product_special_type](product_special_type/) | 1.0 (unported) | Product Special Types
[product_special_type_invoice](product_special_type_invoice/) | 1.0 (unported) | Product Special Type on Invoice
[product_special_type_sale](product_special_type_sale/) | 1.0 (unported) | Product Special Type on Sale
[sale_condition_text](sale_condition_text/) | 1.3 (unported) | Sale/invoice condition
[sale_delivery_term](sale_delivery_term/) | 0.1 (unported) | Delivery term for sale orders
[sale_dropshipping](sale_dropshipping/) | 1.1.1 (unported) | Sale Dropshipping
[sale_exception_nostock](sale_exception_nostock/) | 8.0.1.2.0 (unported) | Sale stock exception
[sale_jit_on_services](sale_jit_on_services/) | 1.0 (unported) | Sale Service Just In Time
[sale_last_price_info](sale_last_price_info/) | 8.0.1.0.0 (unported) | Product Last Price Info - Sale
[sale_multi_picking](sale_multi_picking/) | 0.1 (unported) | Multi Pickings from Sale Orders
[sale_order_force_number](sale_order_force_number/) | 0.1 (unported) | Force sale orders numeration
[sale_order_line_description](sale_order_line_description/) | 8.0.1.0.0 (unported) | Sale order line description
[sale_order_revision](sale_order_revision/) | 8.0.0.1.0 (unported) | Sale order revisions
[sale_owner_stock_sourcing](sale_owner_stock_sourcing/) | 8.0.0.1.0 (unported) | Manage stock ownership on sale order lines
[sale_partner_order_policy](sale_partner_order_policy/) | 8.0.1.0.0 (unported) | Adds customer create invoice method on partner form
[sale_payment_term_interest](sale_payment_term_interest/) | 8.0.1.0.0 (unported) | Sales Payment Term Interests
[sale_product_set_layout](sale_product_set_layout/) | 8.0.1.0.0 (unported) | Sale product set layout
[sale_quotation_number](sale_quotation_number/) | 8.0.1.1.0 (unported) | Different sequence for sale quotations
[sale_quotation_sourcing](sale_quotation_sourcing/) | 8.0.0.3.1 (unported) | manual sourcing of sale quotations
[sale_quotation_sourcing_stock_route_transit](sale_quotation_sourcing_stock_route_transit/) | 8.0.0.1.0 (unported) | Link module for sale_quotation_sourcing + stock_route_transit
[sale_reason_to_export](sale_reason_to_export/) | 8.0.0.1.0 (unported) | Reason to export in Sales Order
[sale_sourced_by_line_sale_transport_multi_address](sale_sourced_by_line_sale_transport_multi_address/) | 8.0.1.0.0 (unported) | Make sale_sourced_by_line and sale_transport_multi_addresswork together
[sale_stock_global_delivery_lead_time](sale_stock_global_delivery_lead_time/) | 0.1 (unported) | Sale global delivery lead time

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-sale-workflow-9-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-sale-workflow-9-0)
