[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/167/13.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-sale-workflow-167)
[![Build Status](https://travis-ci.org/OCA/sale-workflow.svg?branch=13.0)](https://travis-ci.org/OCA/sale-workflow)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)

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
[partner_sale_pivot](partner_sale_pivot/) | 13.0.1.0.0 | Sales analysis from customer form view
[portal_sale_personal_data_only](portal_sale_personal_data_only/) | 13.0.1.1.0 | Portal Sale Personal Data Only
[sale_automatic_workflow](sale_automatic_workflow/) | 13.0.1.2.2 | Sale Automatic Workflow
[sale_automatic_workflow_payment](sale_automatic_workflow_payment/) | 13.0.1.0.0 | Assign a workflow if a transaction is created for a sale order with an acquirer with a workflow
[sale_blanket_order](sale_blanket_order/) | 13.0.1.0.1 | Blanket Orders
[sale_by_packaging](sale_by_packaging/) | 13.0.1.5.1 | Manage sale of packaging
[sale_cancel_reason](sale_cancel_reason/) | 13.0.1.0.0 | Sale Cancel Reason
[sale_commercial_partner](sale_commercial_partner/) | 13.0.1.0.0 | Add stored related field 'Commercial Entity' on sale orders
[sale_contact_type](sale_contact_type/) | 13.0.1.0.0 | Define ordering contact type
[sale_coupon_most_expensive](sale_coupon_most_expensive/) | 13.0.1.0.1 | Extra Discount Apply option - On Most Expensive Product
[sale_coupon_most_expensive_delivery](sale_coupon_most_expensive_delivery/) | 13.0.1.0.1 | Bridge for Most Expensive program and shipping costs
[sale_coupon_multi_currency](sale_coupon_multi_currency/) | 13.0.1.0.1 | Allow to use custom currency on coupon/promotion program
[sale_coupon_multi_use](sale_coupon_multi_use/) | 13.0.1.0.1 | Allow to use same coupon multiple times
[sale_coupon_multi_use_currency](sale_coupon_multi_use_currency/) | 13.0.1.0.1 | Prevents in changing currency if multi coupon is in use
[sale_coupon_product_management](sale_coupon_product_management/) | 13.0.1.0.0 | Improves related product management via sale coupons
[sale_cutoff_time_delivery](sale_cutoff_time_delivery/) | 13.0.1.2.0 | Schedule delivery orders according to cutoff preferences
[sale_discount_display_amount](sale_discount_display_amount/) | 13.0.1.0.1 | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_elaboration](sale_elaboration/) | 13.0.1.0.0 | Set an elaboration for any sale line
[sale_exception](sale_exception/) | 13.0.1.1.1 | Custom exceptions on sale order
[sale_fixed_discount](sale_fixed_discount/) | 13.0.1.1.1 | Allows to apply fixed amount discounts in sales orders.
[sale_force_invoiced](sale_force_invoiced/) | 13.0.1.1.0 | Allows to force the invoice status of the sales order to Invoiced
[sale_force_whole_invoiceability](sale_force_whole_invoiceability/) | 13.0.1.0.0 | Sale Force Whole Invoiceability
[sale_invoice_plan](sale_invoice_plan/) | 13.0.1.0.2 | Add to sales order, ability to manage future invoice plan
[sale_invoice_policy](sale_invoice_policy/) | 13.0.1.0.1 | Sales Management: let the user choose the invoice policy on the order
[sale_isolated_quotation](sale_isolated_quotation/) | 13.0.1.0.0 | Sale Isolated Quotation
[sale_last_price_info](sale_last_price_info/) | 13.0.1.0.0 | Product Last Price Info - Sale
[sale_manual_delivery](sale_manual_delivery/) | 13.0.1.0.1 | Create manually your deliveries
[sale_order_archive](sale_order_archive/) | 13.0.1.0.0 | Archive Sale Orders
[sale_order_carrier_auto_assign](sale_order_carrier_auto_assign/) | 13.0.1.1.0 | Auto assign delivery carrier on sale order confirmation
[sale_order_general_discount](sale_order_general_discount/) | 13.0.1.0.1 | General discount per sale order
[sale_order_incoterm_place](sale_order_incoterm_place/) | 13.0.1.0.1 | Sale Order Incoterm Place
[sale_order_invoice_amount](sale_order_invoice_amount/) | 13.0.1.0.1 | Display the invoiced and uninvoiced total in the sale order
[sale_order_invoicing_finished_task](sale_order_invoicing_finished_task/) | 13.0.1.0.0 | Control invoice order lines if their related task has been set to invoiceable
[sale_order_line_date](sale_order_line_date/) | 13.0.1.1.0 | Adds a commitment date to each sale order line.
[sale_order_line_description](sale_order_line_description/) | 13.0.1.0.0 | Sale order line description
[sale_order_line_packaging_qty](sale_order_line_packaging_qty/) | 13.0.1.2.2 | Define quantities according to product packaging on sale order lines
[sale_order_line_price_history](sale_order_line_price_history/) | 13.0.1.1.0 | Sale order line price history
[sale_order_lot_selection](sale_order_lot_selection/) | 13.0.1.0.2 | Sale Order Lot Selection
[sale_order_priority](sale_order_priority/) | 13.0.1.0.0 | Define priority on sale orders
[sale_order_product_assortment](sale_order_product_assortment/) | 13.0.1.0.0 | Module that allows to use the assortments on sale orders
[sale_order_product_availability_inline](sale_order_product_availability_inline/) | 13.0.1.1.1 | Show product availability in sales order line product drop-down.
[sale_order_product_recommendation](sale_order_product_recommendation/) | 13.0.3.0.1 | Recommend products to sell to customer based on history
[sale_order_product_recommendation_secondary_unit](sale_order_product_recommendation_secondary_unit/) | 13.0.2.2.0 | Add secondary unit to recommend products wizard
[sale_order_qty_change_no_recompute](sale_order_qty_change_no_recompute/) | 13.0.1.0.1 | Prevent recompute if only quantity has changed in sale order line
[sale_order_revision](sale_order_revision/) | 13.0.1.0.0 | Keep track of revised quotations
[sale_order_secondary_unit](sale_order_secondary_unit/) | 13.0.1.1.0 | Sale product in a secondary unit
[sale_order_tag](sale_order_tag/) | 13.0.1.0.1 | Adds Tags to Sales Orders.
[sale_order_type](sale_order_type/) | 13.0.1.4.0 | Sale Order Type
[sale_order_warn_message](sale_order_warn_message/) | 13.0.1.1.0 | Add a popup warning on sale to ensure warning is populated
[sale_partner_delivery_window](sale_partner_delivery_window/) | 13.0.1.1.0 | Schedule delivery orders according to delivery window preferences
[sale_partner_incoterm](sale_partner_incoterm/) | 13.0.1.0.1 | Set the customer preferred incoterm on each sales order
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 13.0.1.0.3 | Base module for multiple procurement group by Sale order
[sale_product_category_menu](sale_product_category_menu/) | 13.0.1.0.1 | Shows 'Product Categories' menu item in Sales
[sale_product_multi_add](sale_product_multi_add/) | 13.0.1.0.1 | Sale Product Multi Add
[sale_product_set](sale_product_set/) | 13.0.1.2.1 | Sale product set
[sale_product_set_packaging_qty](sale_product_set_packaging_qty/) | 13.0.1.0.1 | Manage packaging and quantities on product set lines
[sale_quotation_number](sale_quotation_number/) | 13.0.1.0.0 | Different sequence for sale quotations
[sale_secondary_salesperson](sale_secondary_salesperson/) | 13.0.1.0.0 | Sale Secondary Salesperson
[sale_shipping_info_helper](sale_shipping_info_helper/) | 13.0.1.0.0 | Add shipping amounts on sale order
[sale_sourced_by_line](sale_sourced_by_line/) | 13.0.1.0.1 | Multiple warehouse source locations for Sale order
[sale_stock_delivery_address](sale_stock_delivery_address/) | 13.0.1.0.3 | Sale Stock Delivery Address
[sale_stock_picking_blocking](sale_stock_picking_blocking/) | 13.0.1.0.1 | Allow you to block the creation of deliveries from a sale order.
[sale_stock_picking_note](sale_stock_picking_note/) | 13.0.1.0.0 | Add picking note in sale and purchase order
[sale_stock_return_request](sale_stock_return_request/) | 13.0.1.0.0 | Sale Stock Return Request
[sale_stock_secondary_unit](sale_stock_secondary_unit/) | 13.0.1.0.0 | Get product quantities in a secondary unit
[sale_tier_validation](sale_tier_validation/) | 13.0.1.0.0 | Extends the functionality of Sale Orders to support a tier validation process.
[sale_validity](sale_validity/) | 13.0.1.0.1 | Set a default validity delay on quotations
[sale_wishlist](sale_wishlist/) | 13.0.1.0.0 | Handle sale wishlist for partners
[sales_team_security](sales_team_security/) | 13.0.1.2.0 | New group for seeing only sales channel's documents

[//]: # (end addons)


Translation Status
------------------

[![Translation status](https://translation.odoo-community.org/widgets/sale-workflow-13-0/-/multi-auto.svg)](https://translation.odoo-community.org/engage/sale-workflow-13-0/?utm_source=widget)

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
