
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/sale-workflow&target_branch=18.0)
[![Pre-commit Status](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=18.0)](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml?query=branch%3A18.0)
[![Build Status](https://github.com/OCA/sale-workflow/actions/workflows/test.yml/badge.svg?branch=18.0)](https://github.com/OCA/sale-workflow/actions/workflows/test.yml?query=branch%3A18.0)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/18.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/sale-workflow-18-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/sale-workflow-18-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# sale-workflow

sale-workflow

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[product_set_sell_only_by_packaging](product_set_sell_only_by_packaging/) | 18.0.1.0.0 |  | Glue module between `sell_only_by_packaging` and `sale_product_set_packaging_qty`.
[sale_automatic_workflow](sale_automatic_workflow/) | 18.0.1.0.0 |  | Sale Automatic Workflow
[sale_automatic_workflow_job](sale_automatic_workflow_job/) | 18.0.1.0.0 |  | Execute sale automatic workflows in queue jobs
[sale_automatic_workflow_periodicity](sale_automatic_workflow_periodicity/) | 18.0.1.0.0 | [![TDu](https://github.com/TDu.png?size=30px)](https://github.com/TDu) | Adds a period for the execution of a workflow.
[sale_automatic_workflow_stock](sale_automatic_workflow_stock/) | 18.0.1.0.0 |  | Sale Automatic Workflow Stock
[sale_cancel_reason](sale_cancel_reason/) | 18.0.1.0.0 |  | Sale Cancel Reason
[sale_commercial_partner](sale_commercial_partner/) | 18.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Add stored related field 'Commercial Entity' on sale orders
[sale_delivery_split_date](sale_delivery_split_date/) | 18.0.1.0.0 |  | Sale Deliveries split by date
[sale_discount_display_amount](sale_discount_display_amount/) | 18.0.1.0.0 |  | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_exception](sale_exception/) | 18.0.1.0.0 |  | Custom exceptions on sale order
[sale_exception_product_sale_manufactured_for](sale_exception_product_sale_manufactured_for/) | 18.0.1.0.0 |  | The partner set in the sales order can order only if he/she has a commercial entity that is listed as one of the partners for which the products can be manufactured for.
[sale_force_invoiced](sale_force_invoiced/) | 18.0.1.0.0 |  | Allows to force the invoice status of the sales order to Invoiced
[sale_mail_autosubscribe](sale_mail_autosubscribe/) | 18.0.1.0.0 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Automatically subscribe partners to their company's sale orders
[sale_order_archive](sale_order_archive/) | 18.0.1.0.0 |  | Archive Sale Orders
[sale_order_disable_user_autosubscribe](sale_order_disable_user_autosubscribe/) | 18.0.1.0.0 |  | Remove the salesperson from autosubscribed sale followers
[sale_order_line_date](sale_order_line_date/) | 18.0.1.0.1 |  | Adds a commitment date to each sale order line.
[sale_order_line_menu](sale_order_line_menu/) | 18.0.1.0.0 |  | Adds a Sale Order Lines Menu
[sale_order_line_note](sale_order_line_note/) | 18.0.1.0.0 |  | Note on sale order line
[sale_order_line_price_history](sale_order_line_price_history/) | 18.0.1.0.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) [![Shide](https://github.com/Shide.png?size=30px)](https://github.com/Shide) | Sale order line price history
[sale_order_line_sequence](sale_order_line_sequence/) | 18.0.1.0.0 |  | Propagates SO line sequence to invoices and stock picking.
[sale_order_lot_selection](sale_order_lot_selection/) | 18.0.1.0.0 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Sale Order Lot Selection
[sale_order_note_template](sale_order_note_template/) | 18.0.1.0.0 |  | Add sale orders terms and conditions template that can be used to quickly fullfill sale order terms and conditions
[sale_order_price_recalculation](sale_order_price_recalculation/) | 18.0.1.0.0 |  | Recalculate prices / Reset descriptions on sale order lines
[sale_order_product_availability_inline](sale_order_product_availability_inline/) | 18.0.1.0.0 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Show product availability in sales order line product drop-down.
[sale_order_report_without_price](sale_order_report_without_price/) | 18.0.1.0.0 |  | Allow you to generate quotation and order reports without price.
[sale_order_requested_delivery](sale_order_requested_delivery/) | 18.0.1.0.0 |  | This module adds two new fields `requested_delivery_period_start` and `requested_delivery_period_end` to both the `sale.order` and `sale.order.line` models.
[sale_order_revision](sale_order_revision/) | 18.0.1.0.0 |  | Keep track of revised quotations
[sale_order_type](sale_order_type/) | 18.0.1.0.0 |  | Sale Order Type
[sale_order_warn_message](sale_order_warn_message/) | 18.0.1.0.0 |  | Add a popup warning on sale to ensure warning is populated
[sale_partner_address_restrict](sale_partner_address_restrict/) | 18.0.1.0.0 |  | Restrict addresses domain in the sales order form taking into account the partner selected
[sale_partner_incoterm](sale_partner_incoterm/) | 18.0.1.0.0 |  | Set the customer preferred incoterm on each sales order
[sale_partner_selectable_option](sale_partner_selectable_option/) | 18.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Sale Partner Selectable Option
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 18.0.1.0.0 |  | Base module for multiple procurement group by Sale order
[sale_product_set](sale_product_set/) | 18.0.1.0.0 |  | Sales product set
[sale_product_set_packaging_qty](sale_product_set_packaging_qty/) | 18.0.1.0.0 |  | Manage packaging and quantities on product set lines
[sale_shipping_info_helper](sale_shipping_info_helper/) | 18.0.1.0.0 |  | Add shipping amounts on sale order
[sale_sourced_by_line](sale_sourced_by_line/) | 18.0.1.0.0 |  | Multiple warehouse source locations for Sale order
[sale_stock_cancel_restriction](sale_stock_cancel_restriction/) | 18.0.1.0.0 |  | Sale Stock Cancel Restriction
[sale_stock_line_customer_ref](sale_stock_line_customer_ref/) | 18.0.1.0.0 | [![sebalix](https://github.com/sebalix.png?size=30px)](https://github.com/sebalix) | Allow you to add a customer reference on order lines propagaged to move operations.
[sale_stock_picking_note](sale_stock_picking_note/) | 18.0.1.0.0 | [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) [![EmilioPascual](https://github.com/EmilioPascual.png?size=30px)](https://github.com/EmilioPascual) | Add picking note in sale and purchase order
[sale_tier_validation](sale_tier_validation/) | 18.0.1.0.0 |  | Extends the functionality of Sale Orders to support a tier validation process.
[sale_wishlist](sale_wishlist/) | 18.0.1.0.0 |  | Handle sale wishlist for partners
[sales_team_security](sales_team_security/) | 18.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | New group for seeing only sales channel's documents
[sell_only_by_packaging](sell_only_by_packaging/) | 18.0.1.0.0 |  | Manage sale of packaging

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
