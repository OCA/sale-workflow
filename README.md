
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/sale-workflow&target_branch=10.0)
[![Pre-commit Status](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=10.0)](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml?query=branch%3A10.0)
[![Build Status](https://github.com/OCA/sale-workflow/actions/workflows/test.yml/badge.svg?branch=10.0)](https://github.com/OCA/sale-workflow/actions/workflows/test.yml?query=branch%3A10.0)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/10.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/sale-workflow-10-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/sale-workflow-10-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Odoo Sales, Workflow and Organization

None

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[portal_sale_personal_data_only](portal_sale_personal_data_only/) | 10.0.1.0.1 |  | Allow portal users to see their own documents
[product_margin_classification](product_margin_classification/) | 10.0.2.0.1 |  | Product Margin Classification
[product_price_category](product_price_category/) | 10.0.1.0.1 |  | Add Price Category field on product and allow to apply a pricelist on this field.
[product_supplierinfo_for_customer_sale](product_supplierinfo_for_customer_sale/) | 10.0.1.0.1 |  | Loads in every sale order line the customer code defined in the product
[sale_automatic_workflow](sale_automatic_workflow/) | 10.0.1.0.2 |  | Sale Automatic Workflow
[sale_automatic_workflow_exception](sale_automatic_workflow_exception/) | 10.0.1.0.1 |  | Sale Automatic Workflow Exception
[sale_automatic_workflow_payment_mode](sale_automatic_workflow_payment_mode/) | 10.0.1.0.3 |  | Sale Automatic Workflow - Payment Mode
[sale_automatic_workflow_payment_ref](sale_automatic_workflow_payment_ref/) | 10.0.1.0.1 |  | Propagates your payment reference from your sale order to your payment
[sale_automatic_workflow_validate_purchase_mto](sale_automatic_workflow_validate_purchase_mto/) | 10.0.1.0.2 |  | When a sale order generates directly a purchase order, validates it automatically
[sale_blanket_order](sale_blanket_order/) | 10.0.1.0.0 |  | Blanket Orders
[sale_cancel_reason](sale_cancel_reason/) | 10.0.1.0.2 |  | Sale Cancel Reason
[sale_commercial_partner](sale_commercial_partner/) | 10.0.1.0.2 |  | Add stored related field 'Commercial Entity' on sale orders
[sale_company_currency](sale_company_currency/) | 10.0.1.0.1 |  | Company currency in sale orders
[sale_delivery_split_date](sale_delivery_split_date/) | 10.0.1.0.0 |  | Sale Deliveries split by date
[sale_discount_display_amount](sale_discount_display_amount/) | 10.0.1.0.1 |  | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_exception](sale_exception/) | 10.0.2.0.2 |  | Custom exceptions on sale order
[sale_fixed_discount](sale_fixed_discount/) | 10.0.1.0.1 |  | Allows to apply fixed amount discounts in sales orders.
[sale_force_invoiced](sale_force_invoiced/) | 10.0.1.0.0 |  | Allows to force the invoice status of the sales order to Invoiced
[sale_invoice_auto_deliver](sale_invoice_auto_deliver/) | 10.0.1.0.1 |  | Sale Invoice Automatic Deliver
[sale_invoice_group_method](sale_invoice_group_method/) | 10.0.1.0.0 |  | Sale Invoice Group Method
[sale_invoice_policy](sale_invoice_policy/) | 10.0.1.0.0 |  | Sales Management: let the user choose the invoice policy on the order
[sale_isolated_quotation](sale_isolated_quotation/) | 10.0.1.0.1 |  | Sales - Isolated Quotation
[sale_layout_hidden](sale_layout_hidden/) | 10.0.1.0.2 |  | Sale Layout Hidden Sections
[sale_manual_delivery](sale_manual_delivery/) | 10.0.2.0.0 |  | Create manually your deliveries
[sale_merge_draft_invoice](sale_merge_draft_invoice/) | 10.0.1.0.0 |  | Sale Merge Draft Invoice
[sale_mrp_link](sale_mrp_link/) | 10.0.1.0.0 |  | Show manufacturing orders generated from sales order
[sale_order_action_invoice_create_hook](sale_order_action_invoice_create_hook/) | 10.0.1.0.0 |  | Sale Order Action Invoice Create Hook
[sale_order_invoicing_finished_task](sale_order_invoicing_finished_task/) | 10.0.1.0.3 |  | Control invoice order lines if his task has been finished
[sale_order_line_confirmation_date](sale_order_line_confirmation_date/) | 10.0.1.0.1 |  | Adds the confrmation date on order lines
[sale_order_line_date](sale_order_line_date/) | 10.0.1.0.1 |  | Sale Order Line Date
[sale_order_line_description](sale_order_line_description/) | 10.0.1.0.1 |  | Sale order line description
[sale_order_line_sequence](sale_order_line_sequence/) | 10.0.1.0.1 |  | Propagates SO line sequence to invoices and stock picking.
[sale_order_lot_generator](sale_order_lot_generator/) | 10.0.0.0.2 |  | sale_order_lot_generator
[sale_order_lot_mrp](sale_order_lot_mrp/) | 10.0.1.0.0 |  | sale_order_lot_mrp
[sale_order_lot_selection](sale_order_lot_selection/) | 10.0.1.0.1 |  | Sale Order Lot Selection
[sale_order_margin_percent](sale_order_margin_percent/) | 10.0.1.0.1 |  | Show Percent in sale order
[sale_order_price_recalculation](sale_order_price_recalculation/) | 10.0.1.0.2 |  | Price recalculation in sales orders
[sale_order_priority](sale_order_priority/) | 10.0.1.0.1 |  | Define priority on sale orders
[sale_order_restrict_cancel_existing_invoice](sale_order_restrict_cancel_existing_invoice/) | 10.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Allows to restrict sale order cancelling if an invoice exists
[sale_order_revision](sale_order_revision/) | 10.0.1.0.2 |  | Sale order revisions
[sale_order_type](sale_order_type/) | 10.0.1.1.0 |  | Sale Order Type
[sale_owner_stock_sourcing](sale_owner_stock_sourcing/) | 10.0.1.0.1 |  | Manage stock ownership on sale order lines
[sale_partner_incoterm](sale_partner_incoterm/) | 10.0.1.0.1 |  | Set the customer preferred incoterm on each sales order
[sale_partner_version](sale_partner_version/) | 10.0.1.0.1 |  | Sale Partner Version
[sale_procurement_amendment](sale_procurement_amendment/) | 10.0.1.0.1 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Allow to reflect confirmed sale lines quantity amendments to procurements
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 10.0.1.1.2 |  | Base module for multiple procurement group by Sale order
[sale_procurement_group_by_requested_date](sale_procurement_group_by_requested_date/) | 10.0.1.0.0 |  | Groups pickings based on requested date of order line
[sale_procurement_group_by_requested_date_sale_sourced_by_line](sale_procurement_group_by_requested_date_sale_sourced_by_line/) | 10.0.1.0.0 |  | Integrates sale_source_by_line and sale procurement group
[sale_product_multi_add](sale_product_multi_add/) | 10.0.1.0.1 |  | Sale Product Multi Add
[sale_product_set](sale_product_set/) | 10.0.1.0.2 |  | Sale product set
[sale_product_set_layout](sale_product_set_layout/) | 10.0.1.0.1 |  | Sale product set layout
[sale_promotion_rule](sale_promotion_rule/) | 10.0.2.1.1 |  | Module to manage promotion rule on sale order
[sale_promotion_rule_assortment](sale_promotion_rule_assortment/) | 10.0.1.0.0 |  | This addon allows to reduce the appliance of a promotion rule to a set of products
[sale_promotion_rule_delivery](sale_promotion_rule_delivery/) | 10.0.1.0.0 |  | Manage promotion rule with delivery
[sale_quotation_number](sale_quotation_number/) | 10.0.1.1.1 |  | Different sequence for sale quotations
[sale_rental](sale_rental/) | 10.0.1.0.1 |  | Manage Rental of Products
[sale_revert_done](sale_revert_done/) | 10.0.1.0.1 |  | This module extends the functionality of sales to allow you to set a sales order done back to state 'Sale Order'.
[sale_shipping_info_helper](sale_shipping_info_helper/) | 10.0.1.0.0 |  | Add shipping amounts on sale order
[sale_sourced_by_line](sale_sourced_by_line/) | 10.0.1.0.0 |  | Multiple warehouse source locations for Sale order
[sale_start_end_dates](sale_start_end_dates/) | 10.0.1.0.1 |  | Adds start date and end date on sale order lines
[sale_stock_picking_blocking](sale_stock_picking_blocking/) | 10.0.1.0.1 |  | Allow you to block the creation of deliveries from a sale order.
[sale_stock_picking_blocking_proc_group_by_line](sale_stock_picking_blocking_proc_group_by_line/) | 10.0.1.0.0 |  | Module that allows module sale_delivery_block to work with sale_procurement_group_by_line
[sale_stock_picking_blocking_sale_manual_delivery](sale_stock_picking_blocking_sale_manual_delivery/) | 10.0.1.0.0 |  | Glue module
[sale_stock_picking_note](sale_stock_picking_note/) | 10.0.1.1.0 |  | Add picking note in sale and purchase order
[sale_triple_discount](sale_triple_discount/) | 10.0.1.1.3 |  | Manage triple discount on sale order lines
[sale_validity](sale_validity/) | 10.0.1.0.1 |  | Set a default validity delay on quotations


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_invoice_reorder_lines](account_invoice_reorder_lines/) | 0.1 (unported) |  | Invoice lines with sequence number
[mail_quotation](mail_quotation/) | 0.1 (unported) |  | Mail quotation
[partner_prepayment](partner_prepayment/) | 8.0.1.0.0 (unported) |  | Option on partner to set prepayment policy
[partner_prospect](partner_prospect/) | 8.0.1.0.0 (unported) |  | Partner Prospect
[pricelist_share_companies](pricelist_share_companies/) | 1.0 (unported) |  | Share pricelist between compagnies, not product
[product_special_type](product_special_type/) | 1.0 (unported) |  | Product Special Types
[product_special_type_invoice](product_special_type_invoice/) | 1.0 (unported) |  | Product Special Type on Invoice
[product_special_type_sale](product_special_type_sale/) | 1.0 (unported) |  | Product Special Type on Sale
[sale_condition_text](sale_condition_text/) | 1.3 (unported) |  | Sale/invoice condition
[sale_delivery_term](sale_delivery_term/) | 0.1 (unported) |  | Delivery term for sale orders
[sale_dropshipping](sale_dropshipping/) | 1.1.1 (unported) |  | Sale Dropshipping
[sale_exception_nostock](sale_exception_nostock/) | 8.0.1.2.0 (unported) |  | Sale stock exception
[sale_fiscal_position_update](sale_fiscal_position_update/) | 1.0 (unported) |  | Changing the fiscal position of a sale order will auto-update sale order lines
[sale_generator](sale_generator/) | 10.0.1.0.2 (unported) |  | Sale Generator
[sale_jit_on_services](sale_jit_on_services/) | 1.0 (unported) |  | Sale Service Just In Time
[sale_last_price_info](sale_last_price_info/) | 8.0.1.0.0 (unported) |  | Product Last Price Info - Sale
[sale_multi_picking](sale_multi_picking/) | 0.1 (unported) |  | Multi Pickings from Sale Orders
[sale_order_add_variants](sale_order_add_variants/) | 8.0.0.1.0 (unported) |  | Add variants from template into sale order
[sale_order_force_number](sale_order_force_number/) | 0.1 (unported) |  | Force sale orders numeration
[sale_packaging_price](sale_packaging_price/) | 9.0.1.0.0 (unported) |  | Sale Packaging Price
[sale_payment_term_interest](sale_payment_term_interest/) | 8.0.1.0.0 (unported) |  | Sales Payment Term Interests
[sale_quotation_sourcing](sale_quotation_sourcing/) | 8.0.0.3.1 (unported) |  | manual sourcing of sale quotations
[sale_quotation_sourcing_stock_route_transit](sale_quotation_sourcing_stock_route_transit/) | 8.0.0.1.0 (unported) |  | Link module for sale_quotation_sourcing + stock_route_transit
[sale_reason_to_export](sale_reason_to_export/) | 8.0.0.1.0 (unported) |  | Reason to export in Sales Order
[sale_sourced_by_line_sale_transport_multi_address](sale_sourced_by_line_sale_transport_multi_address/) | 8.0.1.0.0 (unported) |  | Make sale_sourced_by_line and sale_transport_multi_addresswork together
[sale_stock_global_delivery_lead_time](sale_stock_global_delivery_lead_time/) | 0.1 (unported) |  | Sale global delivery lead time

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
