
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/sale-workflow&target_branch=15.0)
[![Pre-commit Status](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=15.0)](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml?query=branch%3A15.0)
[![Build Status](https://github.com/OCA/sale-workflow/actions/workflows/test.yml/badge.svg?branch=15.0)](https://github.com/OCA/sale-workflow/actions/workflows/test.yml?query=branch%3A15.0)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/15.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/sale-workflow-15-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/sale-workflow-15-0/?utm_source=widget)

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
[partner_contact_sale_info_propagation](partner_contact_sale_info_propagation/) | 15.0.1.0.0 |  | Propagate Salesperson and Sales Channel from Company to Contacts
[sale_advance_payment](sale_advance_payment/) | 15.0.1.0.0 |  | Allow to add advance payments on sales and then use them on invoices
[sale_automatic_workflow](sale_automatic_workflow/) | 15.0.1.0.1 |  | Sale Automatic Workflow
[sale_blanket_order](sale_blanket_order/) | 15.0.1.0.0 |  | Blanket Orders
[sale_commercial_partner](sale_commercial_partner/) | 15.0.1.0.1 |  | Add stored related field 'Commercial Entity' on sale orders
[sale_delivery_state](sale_delivery_state/) | 15.0.1.0.0 |  | Show the delivery state on the sale order
[sale_discount_display_amount](sale_discount_display_amount/) | 15.0.1.0.1 |  | This addon intends to display the amount of the discount computed on sale_order_line and sale_order level
[sale_force_invoiced](sale_force_invoiced/) | 15.0.1.0.0 |  | Allows to force the invoice status of the sales order to Invoiced
[sale_invoice_blocking](sale_invoice_blocking/) | 15.0.1.0.0 |  | Allow you to block the creation of invoices from a sale order.
[sale_invoice_plan](sale_invoice_plan/) | 15.0.1.2.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Add to sales order, ability to manage future invoice plan
[sale_invoice_policy](sale_invoice_policy/) | 15.0.1.0.0 |  | Sales Management: let the user choose the invoice policy on the order
[sale_order_invoice_amount](sale_order_invoice_amount/) | 15.0.1.0.0 |  | Display the invoiced and uninvoiced total in the sale order
[sale_order_line_date](sale_order_line_date/) | 15.0.1.1.0 |  | Adds a commitment date to each sale order line.
[sale_order_qty_change_no_recompute](sale_order_qty_change_no_recompute/) | 15.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Prevent recompute if only quantity has changed in sale order line
[sale_order_type](sale_order_type/) | 15.0.2.0.0 |  | Sale Order Type
[sale_partner_selectable_option](sale_partner_selectable_option/) | 15.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Sale Partner Selectable Option
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 15.0.1.0.1 |  | Base module for multiple procurement group by Sale order
[sale_product_category_menu](sale_product_category_menu/) | 15.0.1.0.0 |  | Shows 'Product Categories' menu item in Sales
[sale_product_multi_add](sale_product_multi_add/) | 15.0.1.0.0 |  | Sale Product Multi Add
[sale_product_set](sale_product_set/) | 15.0.1.0.1 |  | Sale product set
[sale_product_set_layout](sale_product_set_layout/) | 15.0.1.0.1 |  | This module allows to add sections with product sets
[sale_quotation_number](sale_quotation_number/) | 15.0.1.0.1 |  | Different sequence for sale quotations
[sale_rental](sale_rental/) | 15.0.1.0.1 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Manage Rental of Products
[sale_sourced_by_line](sale_sourced_by_line/) | 15.0.1.0.1 |  | Multiple warehouse source locations for Sale order
[sale_start_end_dates](sale_start_end_dates/) | 15.0.1.0.1 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Adds start date and end date on sale order lines
[sale_stock_cancel_restriction](sale_stock_cancel_restriction/) | 15.0.1.0.0 |  | Sale Stock Cancel Restriction
[sale_stock_picking_blocking](sale_stock_picking_blocking/) | 15.0.1.0.1 |  | Allow you to block the creation of deliveries from a sale order.
[sale_tier_validation](sale_tier_validation/) | 15.0.1.0.0 |  | Extends the functionality of Sale Orders to support a tier validation process.
[sales_team_security](sales_team_security/) | 15.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | New group for seeing only sales channel's documents
[sales_team_security_crm](sales_team_security_crm/) | 15.0.1.0.0 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Integrates sales_team_security with crm

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
