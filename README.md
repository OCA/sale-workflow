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
[portal_sale_personal_data_only](portal_sale_personal_data_only/) | 13.0.1.0.0 | Portal Sale Personal Data Only
[sale_automatic_workflow](sale_automatic_workflow/) | 13.0.1.1.1 | Sale Automatic Workflow
[sale_automatic_workflow_payment](sale_automatic_workflow_payment/) | 13.0.1.0.0 | Assign a workflow if a transaction is created for a sale order with an acquirer with a workflow
[sale_by_packaging](sale_by_packaging/) | 13.0.1.4.0 | Manage sale of packaging
[sale_commercial_partner](sale_commercial_partner/) | 13.0.1.0.0 | Add stored related field 'Commercial Entity' on sale orders
[sale_cutoff_time_delivery](sale_cutoff_time_delivery/) | 13.0.1.1.0 | Schedule delivery orders according to cutoff preferences
[sale_discount_display_amount](sale_discount_display_amount/) | 13.0.1.0.1 | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_elaboration](sale_elaboration/) | 13.0.1.0.0 | Set an elaboration for any sale line
[sale_exception](sale_exception/) | 13.0.1.1.0 | Custom exceptions on sale order
[sale_fixed_discount](sale_fixed_discount/) | 13.0.1.1.0 | Allows to apply fixed amount discounts in sales orders.
[sale_force_invoiced](sale_force_invoiced/) | 13.0.1.1.0 | Allows to force the invoice status of the sales order to Invoiced
[sale_invoice_plan](sale_invoice_plan/) | 13.0.1.0.2 | Add to sales order, ability to manage future invoice plan
[sale_isolated_quotation](sale_isolated_quotation/) | 13.0.1.0.0 | Sale Isolated Quotation
[sale_last_price_info](sale_last_price_info/) | 13.0.1.0.0 | Product Last Price Info - Sale
[sale_order_archive](sale_order_archive/) | 13.0.1.0.0 | Archive Sale Orders
[sale_order_carrier_auto_assign](sale_order_carrier_auto_assign/) | 13.0.1.1.0 | Auto assign delivery carrier on sale order confirmation
[sale_order_general_discount](sale_order_general_discount/) | 13.0.1.0.0 | General discount per sale order
[sale_order_line_date](sale_order_line_date/) | 13.0.1.1.0 | Adds a commitment date to each sale order line.
[sale_order_line_packaging_qty](sale_order_line_packaging_qty/) | 13.0.1.2.0 | Define quantities according to product packaging on sale order lines
[sale_order_lot_selection](sale_order_lot_selection/) | 13.0.1.0.0 | Sale Order Lot Selection
[sale_order_product_availability_inline](sale_order_product_availability_inline/) | 13.0.1.1.1 | Show product availability in sales order line product drop-down.
[sale_order_product_recommendation](sale_order_product_recommendation/) | 13.0.2.0.5 | Recommend products to sell to customer based on history
[sale_order_product_recommendation_secondary_unit](sale_order_product_recommendation_secondary_unit/) | 13.0.2.0.0 | Add secondary unit to recommend products wizard
[sale_order_revision](sale_order_revision/) | 13.0.1.0.0 | Keep track of revised quotations
[sale_order_secondary_unit](sale_order_secondary_unit/) | 13.0.1.0.0 | Sale product in a secondary unit
[sale_order_type](sale_order_type/) | 13.0.1.3.6 | Sale Order Type
[sale_order_warn_message](sale_order_warn_message/) | 13.0.1.0.0 | Add a popup warning on sale to ensure warning is populated
[sale_partner_incoterm](sale_partner_incoterm/) | 13.0.1.0.1 | Set the customer preferred incoterm on each sales order
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 13.0.1.0.1 | Base module for multiple procurement group by Sale order
[sale_product_category_menu](sale_product_category_menu/) | 13.0.1.0.1 | Shows 'Product Categories' menu item in Sales
[sale_product_multi_add](sale_product_multi_add/) | 13.0.1.0.0 | Sale Product Multi Add
[sale_product_set](sale_product_set/) | 13.0.1.1.0 | Sale product set
[sale_product_set_packaging_qty](sale_product_set_packaging_qty/) | 13.0.1.0.1 | Manage packaging and quantities on product set lines
[sale_quotation_number](sale_quotation_number/) | 13.0.1.0.0 | Different sequence for sale quotations
[sale_shipping_info_helper](sale_shipping_info_helper/) | 13.0.1.0.0 | Add shipping amounts on sale order
[sale_sourced_by_line](sale_sourced_by_line/) | 13.0.1.0.1 | Multiple warehouse source locations for Sale order
[sale_stock_delivery_address](sale_stock_delivery_address/) | 13.0.1.0.3 | Sale Stock Delivery Address
[sale_stock_picking_note](sale_stock_picking_note/) | 13.0.1.0.0 | Add picking note in sale and purchase order
[sale_stock_secondary_unit](sale_stock_secondary_unit/) | 13.0.1.0.0 | Get product quantities in a secondary unit
[sale_tier_validation](sale_tier_validation/) | 13.0.1.0.0 | Extends the functionality of Sale Orders to support a tier validation process.
[sale_validity](sale_validity/) | 13.0.1.0.1 | Set a default validity delay on quotations
[sale_wishlist](sale_wishlist/) | 13.0.1.0.0 | Handle sale wishlist for partners
[sales_team_security](sales_team_security/) | 13.0.1.1.0 | New group for seeing only sales channel's documents

[//]: # (end addons)


Translation Status
------------------

[![Translation status](https://translation.odoo-community.org/widgets/sale-workflow-13-0/-/multi-auto.svg)](https://translation.odoo-community.org/engage/sale-workflow-13-0/?utm_source=widget)

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
