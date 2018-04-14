[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/167/8.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-sale-workflow-167)
[![Build Status](https://travis-ci.org/OCA/sale-workflow.svg?branch=8.0)](https://travis-ci.org/OCA/sale-workflow)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/8.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)

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
[account_invoice_reorder_lines](account_invoice_reorder_lines/) | 8.0.1.0.0 | Provide a new field on the invoice line form, allowing to manage the lines order.
[partner_prepayment](partner_prepayment/) | 8.0.1.0.0 | Option on partner to set prepayment policy
[partner_prospect](partner_prospect/) | 8.0.1.0.0 | Partner Prospect
[product_margin_classification](product_margin_classification/) | 8.0.1.0.0 | Product Margin Classification
[sale_allotment](sale_allotment/) | 8.0.1.1.0 | Separate the shipment according to allotment partner
[sale_automatic_workflow](sale_automatic_workflow/) | 8.0.0.3.0 | Sale Automatic Workflow
[sale_automatic_workflow_exception](sale_automatic_workflow_exception/) | 8.0.1.0.0 | Sale Automatic Workflow Exception
[sale_cancel_reason](sale_cancel_reason/) | 8.0.1.1.0 | Sale Cancel Reason
[sale_change_price](sale_change_price/) | 8.0.1.0.0 | Sale Change Price
[sale_comment_propagation](sale_comment_propagation/) | 8.0.1.0.0 | Comments for sale documents (order, picking and invoice)
[sale_delivery_split_date](sale_delivery_split_date/) | 8.0.1.0.0 | Sale Deliveries split by date
[sale_exception_nostock](sale_exception_nostock/) | 8.0.1.2.0 | Sale stock exception
[sale_exceptions](sale_exceptions/) | 8.0.1.0.0 | Custom exceptions on sale order
[sale_last_price_info](sale_last_price_info/) | 8.0.1.0.0 | Product Last Price Info - Sale
[sale_line_price_properties_based](sale_line_price_properties_based/) | 8.0.1.0.0 | Sale line price properties based
[sale_line_quantity_properties_based](sale_line_quantity_properties_based/) | 8.0.1.0.0 | Sale line quantity properties based
[sale_order_add_variants](sale_order_add_variants/) | 8.0.0.1.0 | Add variants from template into sale order
[sale_order_back2draft](sale_order_back2draft/) | 8.0.1.0.0 | Back to draft on sales orders
[sale_order_calendar_event](sale_order_calendar_event/) | 8.0.1.0.0 | Allows you to attach appointments related to sale orders to the order itself
[sale_order_line_date](sale_order_line_date/) | 8.0.1.0.0 | Sale Order Line Date
[sale_order_line_description](sale_order_line_description/) | 8.0.1.0.0 | Sale order line description
[sale_order_line_variant_description](sale_order_line_variant_description/) | 8.0.1.0.0 | Sale order line variant description
[sale_order_lot_selection](sale_order_lot_selection/) | 8.0.1.0.0 | Sale Order Lot Selection
[sale_order_merge](sale_order_merge/) | 8.0.1.0.0 | Merge sale orders that are confirmed, invoiced or delivered
[sale_order_price_recalculation](sale_order_price_recalculation/) | 8.0.1.0.0 | Price recalculation in sales orders
[sale_order_revision](sale_order_revision/) | 8.0.0.1.0 | Sale order revisions
[sale_order_type](sale_order_type/) | 8.0.1.1.0 | Sale Order Types
[sale_order_type_sale_journal](sale_order_type_sale_journal/) | 8.0.1.0.0 | Link module between sale_order_type and sale_journal
[sale_order_unified_menu](sale_order_unified_menu/) | 8.0.1.0.0 | Sale Order Unified Menu
[sale_order_weight](sale_order_weight/) | 8.0.1.0.0 | Sale Order Weight
[sale_owner_stock_sourcing](sale_owner_stock_sourcing/) | 8.0.0.1.0 | Manage stock ownership on sale order lines
[sale_packaging_price](sale_packaging_price/) | 8.0.1.0.0 | Sale Packaging Price
[sale_partner_incoterm](sale_partner_incoterm/) | 8.0.1.0.0 | Set the customer preferred incoterm on each sales order
[sale_partner_order_policy](sale_partner_order_policy/) | 8.0.1.0.0 | Adds customer create invoice method on partner form
[sale_payment_method](sale_payment_method/) | 8.0.0.2.1 | Sale Payment Method
[sale_payment_method_automatic_workflow](sale_payment_method_automatic_workflow/) | 8.0.1.0.0 | Sale Payment Method - Automatic Worflow (link module)
[sale_payment_method_transaction_id](sale_payment_method_transaction_id/) | 8.0.1.0.0 | Sale Payment Method - Transaction ID Compatibility
[sale_payment_term_interest](sale_payment_term_interest/) | 8.0.1.0.0 | Sales Payment Term Interests
[sale_pricelist_discount](sale_pricelist_discount/) | 8.0.1.0.0 | Sale Pricelist Discount
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 8.0.1.0.0 | Base module for multiple procurement group by Sale order
[sale_product_multi_add](sale_product_multi_add/) | 8.0.1.0.0 | Sale Product Multi Add
[sale_product_set](sale_product_set/) | 8.0.1.0.0 | Sale product set
[sale_product_set_layout](sale_product_set_layout/) | 8.0.1.0.0 | Sale product set layout
[sale_properties_dynamic_fields](sale_properties_dynamic_fields/) | 8.0.1.0.0 | Sale properties dynamic fields
[sale_properties_easy_creation](sale_properties_easy_creation/) | 8.0.1.0.0 | Easing properties input in sale order line
[sale_quick_payment](sale_quick_payment/) | 8.0.3.0.0 | Sale Quick Payment
[sale_quotation_number](sale_quotation_number/) | 8.0.1.1.0 | Different sequence for sale quotations
[sale_quotation_sourcing](sale_quotation_sourcing/) | 8.0.0.3.1 | manual sourcing of sale quotations
[sale_quotation_sourcing_stock_route_transit](sale_quotation_sourcing_stock_route_transit/) | 8.0.0.1.0 | Link module for sale_quotation_sourcing + stock_route_transit
[sale_reason_to_export](sale_reason_to_export/) | 8.0.0.1.0 | Reason to export in Sales Order
[sale_rental](sale_rental/) | 8.0.0.1.0 | Manage Rental of Products
[sale_service_fleet](sale_service_fleet/) | 8.0.1.0.0 | Sale Service Fleet
[sale_service_project](sale_service_project/) | 8.0.1.1.1 | Sale Service Project
[sale_sourced_by_line](sale_sourced_by_line/) | 8.0.1.1.0 | Multiple warehouse source locations for Sale order
[sale_sourced_by_line_sale_transport_multi_address](sale_sourced_by_line_sale_transport_multi_address/) | 8.0.1.0.0 | Make sale_sourced_by_line and sale_transport_multi_addresswork together
[sale_start_end_dates](sale_start_end_dates/) | 8.0.0.1.0 | Adds start date and end date on sale order lines
[sale_validity](sale_validity/) | 8.0.7.0.0 | Sales Quotation Validity Date
[sales_team_security](sales_team_security/) | 8.0.1.0.0 | Sales teams security


Unported addons
---------------
addon | version | summary
--- | --- | ---
[mail_quotation](mail_quotation/) | 0.1 (unported) | Mail quotation
[pricelist_share_companies](pricelist_share_companies/) | 1.0 (unported) | Share pricelist between compagnies, not product
[product_customer_code_sale](product_customer_code_sale/) | 1.0 (unported) | Product Customer code on sale
[product_special_type](product_special_type/) | 1.0 (unported) | Product Special Types
[product_special_type_invoice](product_special_type_invoice/) | 1.0 (unported) | Product Special Type on Invoice
[product_special_type_sale](product_special_type_sale/) | 1.0 (unported) | Product Special Type on Sale
[sale_condition_text](sale_condition_text/) | 1.3 (unported) | Sale/invoice condition
[sale_delivery_term](sale_delivery_term/) | 0.1 (unported) | Delivery term for sale orders
[sale_dropshipping](sale_dropshipping/) | 1.1.1 (unported) | Sale Dropshipping
[sale_fiscal_position_update](sale_fiscal_position_update/) | 1.0 (unported) | Changing the fiscal position of a sale order will auto-update sale order lines
[sale_jit_on_services](sale_jit_on_services/) | 1.0 (unported) | Sale Service Just In Time
[sale_multi_picking](sale_multi_picking/) | 0.1 (unported) | Multi Pickings from Sale Orders
[sale_order_force_number](sale_order_force_number/) | 0.1 (unported) | Force sale orders numeration
[sale_stock_global_delivery_lead_time](sale_stock_global_delivery_lead_time/) | 0.1 (unported) | Sale global delivery lead time

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-sale-workflow-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-sale-workflow-8-0)
