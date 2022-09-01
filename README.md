
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/sale-workflow&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/sale-workflow/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/sale-workflow/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/sale-workflow-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/sale-workflow-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Odoo Sales, Workflow and Organization

This project aim to deal with modules related to manage sale and their related workflow. You'll find modules that:

 - Allow to group discounts / advances / fees separately
 - Add a condition on sales that is pushed on related invoices
 - Compute shipped rate differently
 - Easy the cancellation of SO
 - ...

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[partner_contact_sale_info_propagation](partner_contact_sale_info_propagation/) | 13.0.1.0.1 |  | Propagate Salesperson and Sales Channel from Company to Contacts
[partner_prospect](partner_prospect/) | 13.0.1.0.0 |  | Partner Prospect
[partner_sale_pivot](partner_sale_pivot/) | 13.0.1.1.0 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Sales analysis from customer form view
[portal_sale_personal_data_only](portal_sale_personal_data_only/) | 13.0.1.1.0 |  | Portal Sale Personal Data Only
[product_form_sale_link](product_form_sale_link/) | 13.0.1.0.1 |  | Adds a button on product forms to access Sale Lines
[product_supplierinfo_for_customer_sale](product_supplierinfo_for_customer_sale/) | 13.0.1.3.0 |  | Loads in every sale order line the customer code defined in the product
[sale_advance_payment](sale_advance_payment/) | 13.0.1.0.0 |  | Allow to add advance payments on sales and then use them on invoices
[sale_automatic_workflow](sale_automatic_workflow/) | 13.0.2.1.1 |  | Sale Automatic Workflow
[sale_automatic_workflow_delivery_state](sale_automatic_workflow_delivery_state/) | 13.0.1.0.1 |  | Glue module for sale_automatic_workflow and sale_delivery_state
[sale_automatic_workflow_job](sale_automatic_workflow_job/) | 13.0.1.0.0 |  | Execute sale automatic workflows in queue jobs
[sale_automatic_workflow_payment](sale_automatic_workflow_payment/) | 13.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Assign a workflow if a transaction is created for a sale order with an acquirer with a workflow
[sale_automatic_workflow_payment_mode](sale_automatic_workflow_payment_mode/) | 13.0.1.1.1 |  | Sale Automatic Workflow - Payment Mode
[sale_blanket_order](sale_blanket_order/) | 13.0.1.2.1 |  | Blanket Orders
[sale_by_packaging](sale_by_packaging/) | 13.0.1.6.1 |  | Manage sale of packaging
[sale_cancel_reason](sale_cancel_reason/) | 13.0.1.0.0 |  | Sale Cancel Reason
[sale_commercial_partner](sale_commercial_partner/) | 13.0.1.0.0 |  | Add stored related field 'Commercial Entity' on sale orders
[sale_contact_type](sale_contact_type/) | 13.0.1.0.0 |  | Define ordering contact type
[sale_coupon_most_expensive](sale_coupon_most_expensive/) | 13.0.1.0.1 |  | Extra Discount Apply option - On Most Expensive Product
[sale_coupon_most_expensive_delivery](sale_coupon_most_expensive_delivery/) | 13.0.1.0.1 |  | Bridge for Most Expensive program and shipping costs
[sale_coupon_multi_currency](sale_coupon_multi_currency/) | 13.0.1.0.3 |  | Allow to use custom currency on coupon/promotion program
[sale_coupon_multi_use](sale_coupon_multi_use/) | 13.0.1.0.2 |  | Allow to use same coupon multiple times
[sale_coupon_multi_use_currency](sale_coupon_multi_use_currency/) | 13.0.1.0.1 |  | Prevents in changing currency if multi coupon is in use
[sale_coupon_product_management](sale_coupon_product_management/) | 13.0.1.0.0 |  | Improves related product management via sale coupons
[sale_cutoff_time_delivery](sale_cutoff_time_delivery/) | 13.0.1.4.1 |  | Schedule delivery orders according to cutoff preferences
[sale_delivery_state](sale_delivery_state/) | 13.0.1.0.1 |  | Show the delivery state on the sale order
[sale_discount_display_amount](sale_discount_display_amount/) | 13.0.1.0.2 |  | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_elaboration](sale_elaboration/) | 13.0.1.1.0 |  | Set an elaboration for any sale line
[sale_exception](sale_exception/) | 13.0.1.2.0 |  | Custom exceptions on sale order
[sale_fixed_discount](sale_fixed_discount/) | 13.0.1.1.1 |  | Allows to apply fixed amount discounts in sales orders.
[sale_force_invoiced](sale_force_invoiced/) | 13.0.1.2.0 |  | Allows to force the invoice status of the sales order to Invoiced
[sale_force_whole_invoiceability](sale_force_whole_invoiceability/) | 13.0.1.0.0 |  | Sale Force Whole Invoiceability
[sale_global_discount](sale_global_discount/) | 13.0.1.0.3 |  | Sale Global Discount
[sale_invoice_plan](sale_invoice_plan/) | 13.0.1.0.3 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Add to sales order, ability to manage future invoice plan
[sale_invoice_policy](sale_invoice_policy/) | 13.0.1.0.1 |  | Sales Management: let the user choose the invoice policy on the order
[sale_isolated_quotation](sale_isolated_quotation/) | 13.0.1.1.0 |  | Sale Isolated Quotation
[sale_last_price_info](sale_last_price_info/) | 13.0.1.0.0 |  | Product Last Price Info - Sale
[sale_manual_delivery](sale_manual_delivery/) | 13.0.1.0.2 |  | Create manually your deliveries
[sale_order_archive](sale_order_archive/) | 13.0.1.0.0 |  | Archive Sale Orders
[sale_order_carrier_auto_assign](sale_order_carrier_auto_assign/) | 13.0.1.1.0 |  | Auto assign delivery carrier on sale order confirmation
[sale_order_disable_user_autosubscribe](sale_order_disable_user_autosubscribe/) | 13.0.1.0.0 |  | Remove the salesperson from autosubscribed sale followers
[sale_order_general_discount](sale_order_general_discount/) | 13.0.1.0.1 |  | General discount per sale order
[sale_order_incoterm_place](sale_order_incoterm_place/) | 13.0.1.0.1 |  | Sale Order Incoterm Place
[sale_order_invoice_amount](sale_order_invoice_amount/) | 13.0.1.0.1 |  | Display the invoiced and uninvoiced total in the sale order
[sale_order_invoicing_finished_task](sale_order_invoicing_finished_task/) | 13.0.1.1.0 |  | Control invoice order lines if their related task has been set to invoiceable
[sale_order_line_chained_move](sale_order_line_chained_move/) | 13.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | This module adds a field on sale order line to get all related move lines
[sale_order_line_date](sale_order_line_date/) | 13.0.1.1.0 |  | Adds a commitment date to each sale order line.
[sale_order_line_delivery_state](sale_order_line_delivery_state/) | 13.0.1.0.0 |  | Show the delivery state on the sale order line
[sale_order_line_description](sale_order_line_description/) | 13.0.1.0.0 |  | Sale order line description
[sale_order_line_input](sale_order_line_input/) | 13.0.1.1.2 |  | Search, create or modify directly sale order lines
[sale_order_line_packaging_qty](sale_order_line_packaging_qty/) | 13.0.1.3.1 |  | Define quantities according to product packaging on sale order lines
[sale_order_line_price_history](sale_order_line_price_history/) | 13.0.1.1.0 |  | Sale order line price history
[sale_order_line_sequence](sale_order_line_sequence/) | 13.0.1.0.1 |  | Propagates SO line sequence to invoices and stock picking.
[sale_order_lot_selection](sale_order_lot_selection/) | 13.0.2.1.0 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Sale Order Lot Selection
[sale_order_partner_restrict](sale_order_partner_restrict/) | 13.0.1.0.0 | [![OriolVForgeFlow](https://github.com/OriolVForgeFlow.png?size=30px)](https://github.com/OriolVForgeFlow) | Apply restrictions when selecting from the list of customers on SO.
[sale_order_price_recalculation](sale_order_price_recalculation/) | 13.0.1.1.0 |  | Recalculate prices / Reset descriptions on sale order lines
[sale_order_pricelist_tracking](sale_order_pricelist_tracking/) | 13.0.1.0.0 |  | Track sale order pricelist changes
[sale_order_priority](sale_order_priority/) | 13.0.1.0.0 |  | Define priority on sale orders
[sale_order_product_assortment](sale_order_product_assortment/) | 13.0.1.2.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | Module that allows to use the assortments on sale orders
[sale_order_product_availability_inline](sale_order_product_availability_inline/) | 13.0.1.1.1 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Show product availability in sales order line product drop-down.
[sale_order_product_recommendation](sale_order_product_recommendation/) | 13.0.3.1.1 |  | Recommend products to sell to customer based on history
[sale_order_product_recommendation_secondary_unit](sale_order_product_recommendation_secondary_unit/) | 13.0.2.2.0 |  | Add secondary unit to recommend products wizard
[sale_order_qty_change_no_recompute](sale_order_qty_change_no_recompute/) | 13.0.1.0.3 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Prevent recompute if only quantity has changed in sale order line
[sale_order_revision](sale_order_revision/) | 13.0.1.0.0 |  | Keep track of revised quotations
[sale_order_secondary_unit](sale_order_secondary_unit/) | 13.0.1.2.0 |  | Sale product in a secondary unit
[sale_order_tag](sale_order_tag/) | 13.0.1.0.1 | [![patrickrwilson](https://github.com/patrickrwilson.png?size=30px)](https://github.com/patrickrwilson) | Adds Tags to Sales Orders.
[sale_order_type](sale_order_type/) | 13.0.1.7.3 |  | Sale Order Type
[sale_order_warn_message](sale_order_warn_message/) | 13.0.1.1.0 |  | Add a popup warning on sale to ensure warning is populated
[sale_partner_delivery_window](sale_partner_delivery_window/) | 13.0.1.3.0 |  | Schedule delivery orders according to delivery window preferences
[sale_partner_incoterm](sale_partner_incoterm/) | 13.0.1.0.1 |  | Set the customer preferred incoterm on each sales order
[sale_partner_selectable_option](sale_partner_selectable_option/) | 13.0.2.4.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Sale Partner Selectable Option
[sale_payment_sheet](sale_payment_sheet/) | 13.0.1.1.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Allow to create invoice payments to commercial users without accounting permissions
[sale_procurement_amendment](sale_procurement_amendment/) | 13.0.1.0.2 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Allow to reflect confirmed sale lines quantity amendments to procurements
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 13.0.1.0.5 |  | Base module for multiple procurement group by Sale order
[sale_product_category_menu](sale_product_category_menu/) | 13.0.1.0.1 |  | Shows 'Product Categories' menu item in Sales
[sale_product_multi_add](sale_product_multi_add/) | 13.0.1.0.1 |  | Sale Product Multi Add
[sale_product_set](sale_product_set/) | 13.0.1.4.1 |  | Sale product set
[sale_product_set_packaging_qty](sale_product_set_packaging_qty/) | 13.0.1.0.1 |  | Manage packaging and quantities on product set lines
[sale_product_set_sale_by_packaging](sale_product_set_sale_by_packaging/) | 13.0.1.1.0 |  | Glue module between `sale_by_packaging` and `sale_product_set_packaging_qty`.
[sale_quotation_number](sale_quotation_number/) | 13.0.1.0.0 |  | Different sequence for sale quotations
[sale_resource_booking](sale_resource_booking/) | 13.0.1.0.0 | [![Yajo](https://github.com/Yajo.png?size=30px)](https://github.com/Yajo) | Link resource bookings with sales
[sale_secondary_salesperson](sale_secondary_salesperson/) | 13.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Sale Secondary Salesperson
[sale_shipping_info_helper](sale_shipping_info_helper/) | 13.0.1.0.0 |  | Add shipping amounts on sale order
[sale_sourced_by_line](sale_sourced_by_line/) | 13.0.1.1.0 |  | Multiple warehouse source locations for Sale order
[sale_stock_cancel_restriction](sale_stock_cancel_restriction/) | 13.0.1.0.0 |  | Sale Stock Cancel Restriction
[sale_stock_delivery_address](sale_stock_delivery_address/) | 13.0.1.0.4 |  | Sale Stock Delivery Address
[sale_stock_last_date](sale_stock_last_date/) | 13.0.1.0.0 |  | Displays last delivery date in sale order lines
[sale_stock_picking_blocking](sale_stock_picking_blocking/) | 13.0.1.1.0 |  | Allow you to block the creation of deliveries from a sale order.
[sale_stock_picking_note](sale_stock_picking_note/) | 13.0.2.0.0 |  | Add picking note in sale and purchase order
[sale_stock_picking_validation_blocking](sale_stock_picking_validation_blocking/) | 13.0.1.0.1 |  | This module adds the opportunity to prevent the validation of delivery order from the SO.
[sale_stock_return_request](sale_stock_return_request/) | 13.0.1.0.1 | [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) | Sale Stock Return Request
[sale_stock_secondary_unit](sale_stock_secondary_unit/) | 13.0.1.0.1 |  | Get product quantities in a secondary unit
[sale_tier_validation](sale_tier_validation/) | 13.0.1.1.0 |  | Extends the functionality of Sale Orders to support a tier validation process.
[sale_validity](sale_validity/) | 13.0.1.0.1 |  | Set a default validity delay on quotations
[sale_wishlist](sale_wishlist/) | 13.0.1.0.0 |  | Handle sale wishlist for partners
[sales_team_security](sales_team_security/) | 13.0.3.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | New group for seeing only sales channel's documents

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
