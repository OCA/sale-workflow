[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/167/12.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-sale-workflow-167)
[![Build Status](https://travis-ci.org/OCA/sale-workflow.svg?branch=12.0)](https://travis-ci.org/OCA/sale-workflow)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/12.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)

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
addon | version | maintainers | summary
--- | --- | --- | ---
[partner_contact_sale_info_propagation](partner_contact_sale_info_propagation/) | 12.0.1.0.0 |  | Propagate Salesperson and Sales Channel from Company to Contacts
[partner_prospect](partner_prospect/) | 12.0.1.0.0 |  | Partner Prospect
[partner_sale_pivot](partner_sale_pivot/) | 12.0.1.0.0 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Sales analysis from customer form view
[portal_sale_personal_data_only](portal_sale_personal_data_only/) | 12.0.1.1.0 |  | Allow portal users to see their own documents
[pricelist_by_category_qty](pricelist_by_category_qty/) | 12.0.1.0.0 |  | Discount by quantities of product category
[product_form_sale_link](product_form_sale_link/) | 12.0.1.1.0 |  | Adds a button on product forms to access Sale Lines
[product_supplierinfo_for_customer_sale](product_supplierinfo_for_customer_sale/) | 12.0.1.1.0 |  | Loads in every sale order line the customer code defined in the product
[sale_advance_payment](sale_advance_payment/) | 12.0.1.0.0 |  | Allow to add advance payments on sales and then use them on invoices
[sale_automatic_workflow](sale_automatic_workflow/) | 12.0.1.1.1 |  | Sale Automatic Workflow
[sale_automatic_workflow_job](sale_automatic_workflow_job/) | 12.0.1.0.1 |  | Execute sale automatic workflows in queue jobs
[sale_automatic_workflow_payment_mode](sale_automatic_workflow_payment_mode/) | 12.0.1.0.0 |  | Sale Automatic Workflow - Payment Mode
[sale_blanket_order](sale_blanket_order/) | 12.0.1.0.2 |  | Blanket Orders
[sale_cancel_reason](sale_cancel_reason/) | 12.0.1.2.0 |  | Sale Cancel Reason
[sale_commercial_partner](sale_commercial_partner/) | 12.0.1.0.1 |  | Add stored related field 'Commercial Entity' on sale orders
[sale_commitment_lead_time](sale_commitment_lead_time/) | 12.0.1.0.0 |  | Check preparation time of sale order
[sale_contact_type](sale_contact_type/) | 12.0.1.0.0 |  | Define ordering contact type
[sale_delivery_split_date](sale_delivery_split_date/) | 12.0.1.0.1 |  | Sale Deliveries split by date
[sale_delivery_state](sale_delivery_state/) | 12.0.1.0.0 |  | Show the delivery state on the sale order
[sale_disable_inventory_check](sale_disable_inventory_check/) | 12.0.1.0.0 |  | Disable warning 'Not enough inventory' when there isn't enough product stock
[sale_discount_display_amount](sale_discount_display_amount/) | 12.0.1.1.0 | [![GSLabIt](https://github.com/GSLabIt.png?size=30px)](https://github.com/GSLabIt) | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_double_validation](sale_double_validation/) | 12.0.1.0.1 |  | Double validation for Sales
[sale_elaboration](sale_elaboration/) | 12.0.1.0.1 |  | Set an elaboration for any sale line
[sale_exception](sale_exception/) | 12.0.1.1.1 |  | Custom exceptions on sale order
[sale_fixed_discount](sale_fixed_discount/) | 12.0.1.0.0 |  | Allows to apply fixed amount discounts in sales orders.
[sale_force_invoiced](sale_force_invoiced/) | 12.0.1.0.1 |  | Allows to force the invoice status of the sales order to Invoiced
[sale_force_whole_invoiceability](sale_force_whole_invoiceability/) | 12.0.1.1.0 |  | Sale Force Whole Invoiceability
[sale_generator](sale_generator/) | 12.0.1.0.1 | [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) [![kevinkhao](https://github.com/kevinkhao.png?size=30px)](https://github.com/kevinkhao) | Sale Generator
[sale_global_discount](sale_global_discount/) | 12.0.1.2.1 |  | Sale Global Discount
[sale_invoice_group_method](sale_invoice_group_method/) | 12.0.1.0.0 |  | This module allows you to combine severalSales Orders into a single invoice,if they meet the group criteria defined by the 'Invoice Group Method'
[sale_invoice_plan](sale_invoice_plan/) | 12.0.2.1.2 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Add to sales order, ability to manage future invoice plan
[sale_invoice_policy](sale_invoice_policy/) | 12.0.1.0.0 |  | Sales Management: let the user choose the invoice policy on the order
[sale_isolated_quotation](sale_isolated_quotation/) | 12.0.1.1.0 |  | Sale Isolated Quotation
[sale_last_price_info](sale_last_price_info/) | 12.0.2.0.0 |  | Product Last Price Info - Sale
[sale_manual_delivery](sale_manual_delivery/) | 12.0.2.0.1 |  | Create manually your deliveries
[sale_merge_draft_invoice](sale_merge_draft_invoice/) | 12.0.1.0.1 |  | Sale Merge Draft Invoice
[sale_milestone_profile_invoicing](sale_milestone_profile_invoicing/) | 12.0.1.0.1 |  | Inform on delivered and invoiced work by sale order line.
[sale_mrp_bom](sale_mrp_bom/) | 12.0.1.0.1 |  | Allows define a BOM in the sales lines.
[sale_mrp_link](sale_mrp_link/) | 12.0.1.0.1 |  | Show manufacturing orders generated from sales order
[sale_order_action_invoice_create_hook](sale_order_action_invoice_create_hook/) | 12.0.1.0.3 |  | Add more flexibility in the grouping parameters for the creation of invoices
[sale_order_archive](sale_order_archive/) | 12.0.1.0.0 |  | Archive Sale Orders
[sale_order_digitized_signature](sale_order_digitized_signature/) | 12.0.1.0.0 | [![mgosai](https://github.com/mgosai.png?size=30px)](https://github.com/mgosai) | Capture customer signature on the sales order
[sale_order_general_discount](sale_order_general_discount/) | 12.0.1.1.0 |  | General discount per sale order
[sale_order_incoterm_place](sale_order_incoterm_place/) | 12.0.1.0.1 |  | Sale Order Incoterm Place
[sale_order_invoicing_finished_task](sale_order_invoicing_finished_task/) | 12.0.1.1.1 |  | Control invoice order lines if their related task has been set to invoiceable
[sale_order_line_date](sale_order_line_date/) | 12.0.1.1.1 |  | Adds a commitment date to each sale order line.
[sale_order_line_description](sale_order_line_description/) | 12.0.1.0.0 |  | Sale order line description
[sale_order_line_input](sale_order_line_input/) | 12.0.1.0.0 |  | Search, create or modify directly sale order lines
[sale_order_line_price_history](sale_order_line_price_history/) | 12.0.1.1.1 |  | Sale order line price history
[sale_order_line_sequence](sale_order_line_sequence/) | 12.0.1.0.0 |  | Propagates SO line sequence to invoices and stock picking.
[sale_order_line_serial_unique](sale_order_line_serial_unique/) | 12.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) | Restrict the usage of unique quantity of product per line if product tracking is serial
[sale_order_lot_generator](sale_order_lot_generator/) | 12.0.1.0.2 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) [![mourad-ehm](https://github.com/mourad-ehm.png?size=30px)](https://github.com/mourad-ehm) [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | Sale Order Lot Generator
[sale_order_lot_selection](sale_order_lot_selection/) | 12.0.2.0.1 |  | Sale Order Lot Selection
[sale_order_price_recalculation](sale_order_price_recalculation/) | 12.0.1.1.0 |  | Recalculate prices / Reset descriptions on sale order lines
[sale_order_priority](sale_order_priority/) | 12.0.1.0.1 |  | Define priority on sale orders
[sale_order_product_assortment](sale_order_product_assortment/) | 12.0.1.0.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | Sale Order Product Assortment
[sale_order_product_recommendation](sale_order_product_recommendation/) | 12.0.3.0.1 |  | Recommend products to sell to customer based on history
[sale_order_product_recommendation_secondary_unit](sale_order_product_recommendation_secondary_unit/) | 12.0.2.1.0 |  | Add secondary unit to recommend products wizard
[sale_order_rename](sale_order_rename/) | 12.0.1.0.2 |  | Allows renaming of Quotation / Sale Order
[sale_order_revision](sale_order_revision/) | 12.0.1.0.1 |  | Keep track of revised quotations
[sale_order_secondary_unit](sale_order_secondary_unit/) | 12.0.1.1.0 |  | Sale product in a secondary unit
[sale_order_tag](sale_order_tag/) | 12.0.1.0.0 | [![patrickrwilson](https://github.com/patrickrwilson.png?size=30px)](https://github.com/patrickrwilson) | Adds Tags to Sales Orders.
[sale_order_transmit_method](sale_order_transmit_method/) | 12.0.1.0.0 |  | Set transmit method (email, post, portal, ...) in sale order and propagate it to invoices
[sale_order_type](sale_order_type/) | 12.0.1.3.0 |  | Sale Order Type
[sale_order_weight](sale_order_weight/) | 12.0.1.0.1 |  | Sale Order Weight
[sale_partner_incoterm](sale_partner_incoterm/) | 12.0.1.0.0 |  | Set the customer preferred incoterm on each sales order
[sale_procurement_group_by_commitment_date](sale_procurement_group_by_commitment_date/) | 12.0.1.0.0 |  | Groups pickings based on commitment date of order line
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 12.0.1.0.0 |  | Base module for multiple procurement group by Sale order
[sale_product_category_menu](sale_product_category_menu/) | 12.0.1.0.2 |  | Shows 'Product Categories' menu item in Sales
[sale_product_classification](sale_product_classification/) | 12.0.1.0.0 |  | Classify products regarding their sales performance
[sale_product_multi_add](sale_product_multi_add/) | 12.0.1.1.0 |  | Sale Product Multi Add
[sale_product_returnable](sale_product_returnable/) | 12.0.1.0.2 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Get returnable products from your customers
[sale_product_set](sale_product_set/) | 12.0.1.3.2 |  | Sale product set
[sale_product_set_variant](sale_product_set_variant/) | 12.0.1.1.0 |  | Add variant management to sale product set.
[sale_promotion_rule](sale_promotion_rule/) | 12.0.1.0.1 |  | Module to manage promotion rule on sale order
[sale_quotation_number](sale_quotation_number/) | 12.0.1.0.0 |  | Different sequence for sale quotations
[sale_rental](sale_rental/) | 12.0.1.1.1 |  | Manage Rental of Products
[sale_require_po_doc](sale_require_po_doc/) | 12.0.1.0.1 |  | Sale Orders Require PO or Sales Documentation
[sale_resource_booking](sale_resource_booking/) | 12.0.1.0.0 | [![Yajo](https://github.com/Yajo.png?size=30px)](https://github.com/Yajo) | Link resource bookings with sales
[sale_restricted_qty](sale_restricted_qty/) | 12.0.2.0.0 |  | Sale order min quantity
[sale_secondary_salesperson](sale_secondary_salesperson/) | 12.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Sale Secondary Salesperson
[sale_shipping_info_helper](sale_shipping_info_helper/) | 12.0.1.0.0 |  | Add shipping amounts on sale order
[sale_start_end_dates](sale_start_end_dates/) | 12.0.1.0.1 |  | Adds start date and end date on sale order lines
[sale_stock_delivery_address](sale_stock_delivery_address/) | 12.0.1.0.1 |  | Sale Stock Delivery Address
[sale_stock_last_date](sale_stock_last_date/) | 12.0.1.0.0 |  | Displays last delivery date in sale order lines
[sale_stock_picking_blocking](sale_stock_picking_blocking/) | 12.0.1.0.1 |  | Allow you to block the creation of deliveries from a sale order.
[sale_stock_picking_note](sale_stock_picking_note/) | 12.0.1.0.0 |  | Add picking note in sale and purchase order
[sale_stock_return_request](sale_stock_return_request/) | 12.0.1.0.0 | [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) | Sale Stock Return Request
[sale_stock_secondary_unit](sale_stock_secondary_unit/) | 12.0.1.0.0 |  | Get product quantities in a secondary unit
[sale_stock_sourcing_address](sale_stock_sourcing_address/) | 12.0.1.0.0 |  | Sale Stock Sourcing Address
[sale_substate](sale_substate/) | 12.0.1.0.0 |  | Sale Sub State
[sale_tier_validation](sale_tier_validation/) | 12.0.1.0.0 |  | Extends the functionality of Sale Orders to support a tier validation process.
[sale_triple_discount](sale_triple_discount/) | 12.0.1.1.1 |  | Manage triple discount on sale order lines
[sale_validity](sale_validity/) | 12.0.1.0.0 |  | Set a default validity delay on quotations
[sale_wishlist](sale_wishlist/) | 12.0.1.0.0 |  | Handle sale wishlist for partners
[sales_team_security](sales_team_security/) | 12.0.4.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) | New group for seeing only sales channel's documents

[//]: # (end addons)


Translation Status
------------------

[![Translation status](https://translation.odoo-community.org/widgets/sale-workflow-12-0/-/multi-auto.svg)](https://translation.odoo-community.org/engage/sale-workflow-12-0/?utm_source=widget)

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.
