[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/167/8.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-sale-workflow-167)
[![Build Status](https://travis-ci.org/OCA/sale-workflow.svg?branch=8.0)](https://travis-ci.org/OCA/sale-workflow)
[![Coverage Status](https://coveralls.io/repos/OCA/sale-workflow/badge.png?branch=8.0)](https://coveralls.io/r/OCA/sale-workflow?branch=8.0)

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
[partner_prepayment](partner_prepayment/) | 1.0 | Option on partner to set prepayment policy
[partner_prospect](partner_prospect/) | 1.0 | Partner Prospect
[sale_cancel_reason](sale_cancel_reason/) | 8.0.1.1 | Sale Cancel Reason
[sale_exception_nostock](sale_exception_nostock/) | 1.2 | Sale stock exception
[sale_exceptions](sale_exceptions/) | 1.0 | Custom exceptions on sale order
[sale_last_price_info](sale_last_price_info/) | 1.0 | Product Last Price Info - Sale
[sale_order_add_variants](sale_order_add_variants/) | 0.1 | Add variants from template into sale order
[sale_order_back2draft](sale_order_back2draft/) | 1.0 | Back to draft on sales orders
[sale_order_line_description](sale_order_line_description/) | 1.0 | Sale order line description
[sale_order_price_recalculation](sale_order_price_recalculation/) | 8.0.1.0.0 | Price recalculation in sales orders
[sale_order_revision](sale_order_revision/) | 0.1 | Sale order revisions
[sale_order_type](sale_order_type/) | 8.0.1.0.1 | Sale Order Types
[sale_owner_stock_sourcing](sale_owner_stock_sourcing/) | 0.1 | Manage stock ownership on sale order lines
[sale_partner_order_policy](sale_partner_order_policy/) | 1.0 | Adds customer create invoice method on partner form
[sale_payment_term_interest](sale_payment_term_interest/) | 1.0 | Sales Payment Term Interests
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 1.0 | Base module for multiple procurement group by Sale order
[sale_product_set](sale_product_set/) | 1.0 | Sale product set
[sale_product_set_layout](sale_product_set_layout/) | 1.0 | Sale product set layout
[sale_quotation_number](sale_quotation_number/) | 1.1 | Different sequence for sale quotations
[sale_quotation_sourcing](sale_quotation_sourcing/) | 0.3.1 | manual sourcing of sale quotations
[sale_quotation_sourcing_stock_route_transit](sale_quotation_sourcing_stock_route_transit/) | 0.1 | Link module for sale_quotation_sourcing + stock_route_transit
[sale_reason_to_export](sale_reason_to_export/) | 0.1 | Reason to export in Sales Order
[sale_rental](sale_rental/) | 0.1 | Manage Rental of Products
[sale_sourced_by_line](sale_sourced_by_line/) | 1.1 | Multiple warehouse source locations for Sale order
[sale_sourced_by_line_sale_transport_multi_address](sale_sourced_by_line_sale_transport_multi_address/) | 1.0 | Make sale_sourced_by_line and sale_transport_multi_addresswork together
[sale_start_end_dates](sale_start_end_dates/) | 0.1 | Adds start date and end date on sale order lines
[sale_validity](sale_validity/) | 7.0.0 | Sales Quotation Validity Date

Unported addons
---------------
addon | version | summary
--- | --- | ---
[account_invoice_reorder_lines](__unported__/account_invoice_reorder_lines/) | 0.1 (unported) | Invoice lines with sequence number
[mail_quotation](__unported__/mail_quotation/) | 0.1 (unported) | Mail quotation
[pricelist_share_companies](__unported__/pricelist_share_companies/) | 1.0 (unported) | Share pricelist between compagnies, not product
[product_customer_code_sale](__unported__/product_customer_code_sale/) | 1.0 (unported) | Product Customer code on sale
[product_special_type](__unported__/product_special_type/) | 1.0 (unported) | Product Special Types
[product_special_type_invoice](__unported__/product_special_type_invoice/) | 1.0 (unported) | Product Special Type on Invoice
[product_special_type_sale](__unported__/product_special_type_sale/) | 1.0 (unported) | Product Special Type on Sale
[purchase_order_reorder_lines](__unported__/purchase_order_reorder_lines/) | 0.1 (unported) | Purchase order lines with sequence number
[sale_condition_text](__unported__/sale_condition_text/) | 1.3 (unported) | Sale/invoice condition
[sale_delivery_term](__unported__/sale_delivery_term/) | 0.1 (unported) | Delivery term for sale orders
[sale_dropshipping](__unported__/sale_dropshipping/) | 1.1.1 (unported) | Sale Dropshipping
[sale_fiscal_position_update](__unported__/sale_fiscal_position_update/) | 1.0 (unported) | Changing the fiscal position of a sale order will auto-update sale order lines
[sale_jit_on_services](__unported__/sale_jit_on_services/) | 1.0 (unported) | Sale Service Just In Time
[sale_journal_shop](__unported__/sale_journal_shop/) | 0.0.1 (unported) | Sale Journal Shop
[sale_multi_picking](__unported__/sale_multi_picking/) | 0.1 (unported) | Multi Pickings from Sale Orders
[sale_order_force_number](__unported__/sale_order_force_number/) | 0.1 (unported) | Force sale orders numeration
[sale_stock_global_delivery_lead_time](__unported__/sale_stock_global_delivery_lead_time/) | 0.1 (unported) | Sale global delivery lead time

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-sale-workflow-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-sale-workflow-8-0)
