
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/sale-workflow&target_branch=15.0)
[![Pre-commit Status](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=15.0)](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml?query=branch%3A15.0)
[![Build Status](https://github.com/OCA/sale-workflow/actions/workflows/test.yml/badge.svg?branch=15.0)](https://github.com/OCA/sale-workflow/actions/workflows/test.yml?query=branch%3A15.0)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/15.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/sale-workflow-15-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/sale-workflow-15-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Sale Workflow

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[partner_contact_sale_info_propagation](partner_contact_sale_info_propagation/) | 15.0.1.0.0 |  | Propagate Salesperson and Sales Channel from Company to Contacts
[partner_sale_pivot](partner_sale_pivot/) | 15.0.1.0.0 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Sales analysis from customer form view
[portal_sale_personal_data_only](portal_sale_personal_data_only/) | 15.0.1.0.0 |  | Portal Sale Personal Data Only
[pricelist_cache](pricelist_cache/) | 15.0.1.4.1 |  | Provide a new model to cache price lists and update it, to make it easier to retrieve them.
[product_form_sale_link](product_form_sale_link/) | 15.0.1.0.1 |  | Adds a button on product forms to access Sale Lines
[product_supplierinfo_for_customer_elaboration](product_supplierinfo_for_customer_elaboration/) | 15.0.2.0.2 |  | Allows to define default elaborations and elaboration notes on product customerinfos
[product_supplierinfo_for_customer_sale](product_supplierinfo_for_customer_sale/) | 15.0.1.2.0 |  | Loads in every sale order line the customer code defined in the product
[sale_advance_payment](sale_advance_payment/) | 15.0.1.0.3 |  | Allow to add advance payments on sales and then use them on invoices
[sale_attached_product](sale_attached_product/) | 15.0.1.0.0 | [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) | Define products that will be added automatically when adding another in a sales order
[sale_automatic_workflow](sale_automatic_workflow/) | 15.0.1.0.1 |  | Sale Automatic Workflow
[sale_automatic_workflow_job](sale_automatic_workflow_job/) | 15.0.1.0.0 |  | Execute sale automatic workflows in queue jobs
[sale_automatic_workflow_payment_mode](sale_automatic_workflow_payment_mode/) | 15.0.1.0.0 |  | Sale Automatic Workflow - Payment Mode
[sale_blanket_order](sale_blanket_order/) | 15.0.1.2.1 |  | Blanket Orders
[sale_cancel_reason](sale_cancel_reason/) | 15.0.1.0.0 |  | Sale Cancel Reason
[sale_commercial_partner](sale_commercial_partner/) | 15.0.1.0.2 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Add stored related field 'Commercial Entity' on sale orders
[sale_credit_point](sale_credit_point/) | 15.0.1.0.2 |  | Sale Credit Points
[sale_custom_rounding](sale_custom_rounding/) | 15.0.1.0.1 |  | Custom taxes rounding method in sale orders
[sale_delivery_split_date](sale_delivery_split_date/) | 15.0.1.0.0 |  | Sale Deliveries split by date
[sale_delivery_state](sale_delivery_state/) | 15.0.2.0.0 |  | Show the delivery state on the sale order
[sale_discount_display_amount](sale_discount_display_amount/) | 15.0.1.1.0 |  | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_elaboration](sale_elaboration/) | 15.0.3.3.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Set an elaboration for any sale line
[sale_exception](sale_exception/) | 15.0.1.0.1 |  | Custom exceptions on sale order
[sale_fixed_discount](sale_fixed_discount/) | 15.0.1.0.0 |  | Allows to apply fixed amount discounts in sales orders.
[sale_force_invoiced](sale_force_invoiced/) | 15.0.1.0.0 |  | Allows to force the invoice status of the sales order to Invoiced
[sale_force_whole_invoiceability](sale_force_whole_invoiceability/) | 15.0.1.0.0 |  | Sale Force Whole Invoiceability
[sale_fully_invoiced](sale_fully_invoiced/) | 15.0.1.0.0 |  | Useful filters in Sales to know the actual status of invoices.
[sale_global_discount](sale_global_discount/) | 15.0.1.0.0 |  | Sale Global Discount
[sale_invoice_blocking](sale_invoice_blocking/) | 15.0.1.0.0 |  | Allow you to block the creation of invoices from a sale order.
[sale_invoice_frequency](sale_invoice_frequency/) | 15.0.1.1.1 | [![Shide](https://github.com/Shide.png?size=30px)](https://github.com/Shide) [![yajo](https://github.com/yajo.png?size=30px)](https://github.com/yajo) [![EmilioPascual](https://github.com/EmilioPascual.png?size=30px)](https://github.com/EmilioPascual) | Define the invoice frequency for customers
[sale_invoice_no_mail](sale_invoice_no_mail/) | 15.0.1.0.1 |  | Sale Invoice No Mail
[sale_invoice_plan](sale_invoice_plan/) | 15.0.1.4.2 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Add to sales order, ability to manage future invoice plan
[sale_invoice_policy](sale_invoice_policy/) | 15.0.1.0.1 |  | Sales Management: let the user choose the invoice policy on the order
[sale_last_price_info](sale_last_price_info/) | 15.0.1.0.1 |  | Product Last Price Info - Sale
[sale_missing_tracking](sale_missing_tracking/) | 15.0.1.0.2 | [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) | Tracking sale missing products
[sale_missing_tracking_tier_validation](sale_missing_tracking_tier_validation/) | 15.0.1.0.0 |  | Extends the functionality of Sale missing tracking exceptions to support a tier validation process.
[sale_order_archive](sale_order_archive/) | 15.0.1.0.1 |  | Archive Sale Orders
[sale_order_carrier_auto_assign](sale_order_carrier_auto_assign/) | 15.0.1.0.1 |  | Auto assign delivery carrier on sale order confirmation
[sale_order_discount_invoicing](sale_order_discount_invoicing/) | 15.0.1.0.0 |  | Sale Discount Invoicing
[sale_order_general_discount](sale_order_general_discount/) | 15.0.1.0.1 |  | General discount per sale order
[sale_order_invoice_amount](sale_order_invoice_amount/) | 15.0.1.0.0 |  | Display the invoiced and uninvoiced total in the sale order
[sale_order_invoicing_finished_task](sale_order_invoicing_finished_task/) | 15.0.1.0.1 |  | Control invoice order lines if their related task has been set to invoiceable
[sale_order_line_date](sale_order_line_date/) | 15.0.1.1.0 |  | Adds a commitment date to each sale order line.
[sale_order_line_delivery_state](sale_order_line_delivery_state/) | 15.0.1.0.1 |  | Show the delivery state on the sale order line
[sale_order_line_description](sale_order_line_description/) | 15.0.1.0.0 |  | Sale order line description
[sale_order_line_input](sale_order_line_input/) | 15.0.1.0.2 |  | Search, create or modify directly sale order lines
[sale_order_line_menu](sale_order_line_menu/) | 15.0.1.2.0 |  | Adds a Sale Order Lines Menu
[sale_order_line_note](sale_order_line_note/) | 15.0.1.0.0 |  | Note on sale order line
[sale_order_line_price_history](sale_order_line_price_history/) | 15.0.2.0.2 |  | Sale order line price history
[sale_order_line_remove](sale_order_line_remove/) | 15.0.1.0.0 |  | Allows removal of sale order lines from confirmed orders if not invoiced or received
[sale_order_line_sequence](sale_order_line_sequence/) | 15.0.2.0.0 |  | Propagates SO line sequence to invoices and stock picking.
[sale_order_lot_selection](sale_order_lot_selection/) | 15.0.1.0.0 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Sale Order Lot Selection
[sale_order_partner_restrict](sale_order_partner_restrict/) | 15.0.1.0.0 | [![OriolVForgeFlow](https://github.com/OriolVForgeFlow.png?size=30px)](https://github.com/OriolVForgeFlow) | Apply restrictions when selecting from the list of customers on SO.
[sale_order_price_recalculation](sale_order_price_recalculation/) | 15.0.1.0.0 |  | Recalculate prices / Reset descriptions on sale order lines
[sale_order_priority](sale_order_priority/) | 15.0.1.0.1 |  | Define priority on sale orders
[sale_order_product_assortment](sale_order_product_assortment/) | 15.0.2.0.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | Module that allows to use the assortments on sale orders
[sale_order_product_availability_inline](sale_order_product_availability_inline/) | 15.0.1.0.2 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Show product availability in sales order line product drop-down.
[sale_order_product_recommendation](sale_order_product_recommendation/) | 15.0.1.2.2 |  | Recommend products to sell to customer based on history
[sale_order_product_recommendation_secondary_unit](sale_order_product_recommendation_secondary_unit/) | 15.0.1.0.0 |  | Add secondary unit to recommend products wizard
[sale_order_qty_change_no_recompute](sale_order_qty_change_no_recompute/) | 15.0.2.0.1 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Prevent recompute if only quantity has changed in sale order line
[sale_order_report_without_price](sale_order_report_without_price/) | 15.0.1.0.0 |  | Allow you to generate quotation and order reports without price.
[sale_order_revision](sale_order_revision/) | 15.0.1.0.1 |  | Keep track of revised quotations
[sale_order_secondary_unit](sale_order_secondary_unit/) | 15.0.2.1.0 |  | Sale product in a secondary unit
[sale_order_type](sale_order_type/) | 15.0.2.1.2 |  | Sale Order Type
[sale_order_type_quotation_number](sale_order_type_quotation_number/) | 15.0.1.1.0 |  | Use quotation sequence depending on sale type
[sale_order_warn_message](sale_order_warn_message/) | 15.0.1.0.0 |  | Add a popup warning on sale to ensure warning is populated
[sale_partner_incoterm](sale_partner_incoterm/) | 15.0.1.1.0 |  | Set the customer preferred incoterm on each sales order
[sale_partner_selectable_option](sale_partner_selectable_option/) | 15.0.1.0.2 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Sale Partner Selectable Option
[sale_payment_sheet](sale_payment_sheet/) | 15.0.1.3.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Allow to create invoice payments to commercial users without accounting permissions
[sale_planner_calendar](sale_planner_calendar/) | 15.0.1.7.0 |  | Sale planner calendar
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 15.0.1.2.0 |  | Base module for multiple procurement group by Sale order
[sale_product_category_menu](sale_product_category_menu/) | 15.0.1.0.0 |  | Shows 'Product Categories' menu item in Sales
[sale_product_multi_add](sale_product_multi_add/) | 15.0.1.0.0 |  | Sale Product Multi Add
[sale_product_set](sale_product_set/) | 15.0.1.0.1 |  | Sale product set
[sale_product_set_layout](sale_product_set_layout/) | 15.0.1.0.1 |  | This module allows to add sections with product sets
[sale_purchase_procurement_group_by_line](sale_purchase_procurement_group_by_line/) | 15.0.1.0.0 |  | Glue module between 'MTO Sale <-> Purchase' and 'Sale Procurement Group by Line'
[sale_quotation_number](sale_quotation_number/) | 15.0.2.1.0 |  | Different sequence for sale quotations
[sale_rental](sale_rental/) | 15.0.1.0.2 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Manage Rental of Products
[sale_resource_booking](sale_resource_booking/) | 15.0.1.0.1 | [![Yajo](https://github.com/Yajo.png?size=30px)](https://github.com/Yajo) | Link resource bookings with sales
[sale_shipping_info_helper](sale_shipping_info_helper/) | 15.0.1.0.0 |  | Add shipping amounts on sale order
[sale_sourced_by_line](sale_sourced_by_line/) | 15.0.1.1.0 |  | Multiple warehouse source locations for Sale order
[sale_start_end_dates](sale_start_end_dates/) | 15.0.1.0.1 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Adds start date and end date on sale order lines
[sale_stock_cancel_restriction](sale_stock_cancel_restriction/) | 15.0.1.0.2 |  | Sale Stock Cancel Restriction
[sale_stock_delivery_address](sale_stock_delivery_address/) | 15.0.1.0.0 |  | Sale Stock Delivery Address
[sale_stock_invoice_plan](sale_stock_invoice_plan/) | 15.0.1.0.1 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Add to sales order, ability to manage future invoice plan
[sale_stock_last_date](sale_stock_last_date/) | 15.0.1.0.0 |  | Displays last delivery date in sale order lines
[sale_stock_line_sequence](sale_stock_line_sequence/) | 15.0.1.0.0 |  | Glue Module for Sale Order Line Sequence and Stock Picking Line Sequence
[sale_stock_picking_blocking](sale_stock_picking_blocking/) | 15.0.1.0.1 |  | Allow you to block the creation of deliveries from a sale order.
[sale_stock_picking_note](sale_stock_picking_note/) | 15.0.1.0.1 |  | Add picking note in sale and purchase order
[sale_stock_return_request](sale_stock_return_request/) | 15.0.1.1.1 | [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) | Sale Stock Return Request
[sale_stock_secondary_unit](sale_stock_secondary_unit/) | 15.0.1.0.3 |  | Get product quantities in a secondary unit
[sale_substate](sale_substate/) | 15.0.1.0.0 |  | Sale Sub State
[sale_tier_validation](sale_tier_validation/) | 15.0.1.1.2 |  | Extends the functionality of Sale Orders to support a tier validation process.
[sale_triple_discount](sale_triple_discount/) | 15.0.1.0.1 |  | Manage triple discount on sale order lines
[sale_warn_option](sale_warn_option/) | 15.0.1.0.1 | [![Shide](https://github.com/Shide.png?size=30px)](https://github.com/Shide) [![rafaelbn](https://github.com/rafaelbn.png?size=30px)](https://github.com/rafaelbn) | Add Options to Sale Warn Messages
[sale_wishlist](sale_wishlist/) | 15.0.1.0.0 |  | Handle sale wishlist for partners
[sales_team_security](sales_team_security/) | 15.0.1.0.3 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | New group for seeing only sales channel's documents
[sales_team_security_crm](sales_team_security_crm/) | 15.0.1.0.1 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Integrates sales_team_security with crm
[sales_team_security_sale](sales_team_security_sale/) | 15.0.1.0.1 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Integrates sales_team_security with sale

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
