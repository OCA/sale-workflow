[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/167/14.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-sale-workflow-167)
[![Build Status](https://travis-ci.com/OCA/sale-workflow.svg?branch=14.0)](https://travis-ci.com/OCA/sale-workflow)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/14.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/sale-workflow-14-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/sale-workflow-14-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# sale-workflow

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[product_supplierinfo_for_customer_sale](product_supplierinfo_for_customer_sale/) | 14.0.1.0.1 |  | Loads in every sale order line the customer code defined in the product
[sale_advance_payment](sale_advance_payment/) | 14.0.1.0.0 |  | Allow to add advance payments on sales and then use them on invoices
[sale_automatic_workflow](sale_automatic_workflow/) | 14.0.1.1.2 |  | Sale Automatic Workflow
[sale_automatic_workflow_delivery_state](sale_automatic_workflow_delivery_state/) | 14.0.1.0.0 |  | Glue module for sale_automatic_workflow and sale_delivery_state
[sale_automatic_workflow_payment_mode](sale_automatic_workflow_payment_mode/) | 14.0.1.0.0 |  | Sale Automatic Workflow - Payment Mode
[sale_by_packaging](sale_by_packaging/) | 14.0.1.0.0 |  | Manage sale of packaging
[sale_cancel_confirm](sale_cancel_confirm/) | 14.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Sales Cancel Confirm
[sale_commercial_partner](sale_commercial_partner/) | 14.0.1.0.1 |  | Add stored related field 'Commercial Entity' on sale orders
[sale_commitment_date_mandatory](sale_commitment_date_mandatory/) | 14.0.1.0.0 |  | Set commitment data mandatory and don't allowto add lines unless this field is filled
[sale_delivery_state](sale_delivery_state/) | 14.0.1.0.0 |  | Show the delivery state on the sale order
[sale_discount_display_amount](sale_discount_display_amount/) | 14.0.1.0.2 |  | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_exception](sale_exception/) | 14.0.1.0.1 |  | Custom exceptions on sale order
[sale_force_invoiced](sale_force_invoiced/) | 14.0.1.1.1 |  | Allows to force the invoice status of the sales order to Invoiced
[sale_invoice_blocking](sale_invoice_blocking/) | 14.0.1.0.0 |  | Allow you to block the creation of invoices from a sale order.
[sale_isolated_quotation](sale_isolated_quotation/) | 14.0.1.0.0 | [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Sale Isolated Quotation
[sale_last_price_info](sale_last_price_info/) | 14.0.1.0.1 |  | Product Last Price Info - Sale
[sale_mail_autosubscribe](sale_mail_autosubscribe/) | 14.0.1.0.0 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Automatically subscribe partners to their company's sale orders
[sale_mrp_bom](sale_mrp_bom/) | 14.0.1.0.0 |  | Allows define a BOM in the sales lines.
[sale_order_archive](sale_order_archive/) | 14.0.1.0.0 |  | Archive Sale Orders
[sale_order_carrier_auto_assign](sale_order_carrier_auto_assign/) | 14.0.1.0.1 |  | Auto assign delivery carrier on sale order confirmation
[sale_order_general_discount](sale_order_general_discount/) | 14.0.1.0.0 |  | General discount per sale order
[sale_order_line_date](sale_order_line_date/) | 14.0.1.0.1 |  | Adds a commitment date to each sale order line.
[sale_order_line_description](sale_order_line_description/) | 14.0.1.0.0 |  | Sale order line description
[sale_order_line_menu](sale_order_line_menu/) | 14.0.1.0.0 |  | Adds a Sale Order Lines Menu
[sale_order_line_note](sale_order_line_note/) | 14.0.1.0.0 |  | Note on sale order line
[sale_order_line_packaging_qty](sale_order_line_packaging_qty/) | 14.0.1.0.0 |  | Define quantities according to product packaging on sale order lines
[sale_order_line_price_history](sale_order_line_price_history/) | 14.0.1.0.0 |  | Sale order line price history
[sale_order_lot_generator](sale_order_lot_generator/) | 14.0.1.0.1 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) [![mourad-ehm](https://github.com/mourad-ehm.png?size=30px)](https://github.com/mourad-ehm) [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | Sale Order Lot Generator
[sale_order_lot_selection](sale_order_lot_selection/) | 14.0.1.0.0 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Sale Order Lot Selection
[sale_order_note_template](sale_order_note_template/) | 14.0.1.0.0 |  | Add sale orders terms and conditions template that can be used to quickly fullfill sale order terms and conditions
[sale_order_qty_change_no_recompute](sale_order_qty_change_no_recompute/) | 14.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Prevent recompute if only quantity has changed in sale order line
[sale_order_revision](sale_order_revision/) | 14.0.1.0.0 |  | Keep track of revised quotations
[sale_order_type](sale_order_type/) | 14.0.1.0.1 |  | Sale Order Type
[sale_partner_incoterm](sale_partner_incoterm/) | 14.0.1.0.0 |  | Set the customer preferred incoterm on each sales order
[sale_pricelist_from_commitment_date](sale_pricelist_from_commitment_date/) | 14.0.1.0.1 |  | Use sale order commitment date to compute line price from pricelist
[sale_product_brand_exception](sale_product_brand_exception/) | 14.0.1.0.0 |  | Define rules for sale order and brands
[sale_product_category_menu](sale_product_category_menu/) | 14.0.1.0.1 |  | Shows 'Product Categories' menu item in Sales
[sale_product_multi_add](sale_product_multi_add/) | 14.0.1.0.1 |  | Sale Product Multi Add
[sale_product_rating_verified](sale_product_rating_verified/) | 14.0.1.0.1 |  | Verify if a user has previously bought a product
[sale_product_seasonality](sale_product_seasonality/) | 14.0.1.1.0 |  | Integrates rules for products' seasonal availability with sales
[sale_product_set](sale_product_set/) | 14.0.1.2.0 |  | Sale product set
[sale_product_set_packaging_qty](sale_product_set_packaging_qty/) | 14.0.1.0.0 |  | Manage packaging and quantities on product set lines
[sale_quotation_number](sale_quotation_number/) | 14.0.1.0.2 |  | Different sequence for sale quotations
[sale_shipping_info_helper](sale_shipping_info_helper/) | 14.0.1.0.0 |  | Add shipping amounts on sale order
[sale_start_end_dates](sale_start_end_dates/) | 14.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Adds start date and end date on sale order lines
[sale_stock_picking_blocking](sale_stock_picking_blocking/) | 14.0.1.0.1 |  | Allow you to block the creation of deliveries from a sale order.
[sale_tier_validation](sale_tier_validation/) | 14.0.1.0.0 |  | Extends the functionality of Sale Orders to support a tier validation process.
[sale_validity](sale_validity/) | 14.0.1.0.2 |  | Set a default validity delay on quotations
[sale_wishlist](sale_wishlist/) | 14.0.1.0.1 |  | Handle sale wishlist for partners
[sales_team_security](sales_team_security/) | 14.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | New group for seeing only sales channel's documents
[sales_team_security_crm](sales_team_security_crm/) | 14.0.1.0.0 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Integrates sales_team_security with crm
[sales_team_security_sale](sales_team_security_sale/) | 14.0.1.0.0 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Integrates sales_team_security with sale

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
