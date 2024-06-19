
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/sale-workflow&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/sale-workflow/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/sale-workflow/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/sale-workflow/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/sale-workflow/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/sale-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/sale-workflow-17-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/sale-workflow-17-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# sale-workflow

This project aim to deal with modules related to manage sale and their related workflow.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[partner_sale_pivot](partner_sale_pivot/) | 17.0.1.0.0 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Sales analysis from customer form view
[product_form_sale_link](product_form_sale_link/) | 17.0.1.0.0 |  | Adds a button on product forms to access Sale Lines
[product_supplierinfo_for_customer_sale](product_supplierinfo_for_customer_sale/) | 17.0.1.0.0 |  | Loads in every sale order line the customer code defined in the product
[sale_cancel_reason](sale_cancel_reason/) | 17.0.1.0.0 |  | Sale Cancel Reason
[sale_commercial_partner](sale_commercial_partner/) | 17.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Add stored related field 'Commercial Entity' on sale orders
[sale_delivery_state](sale_delivery_state/) | 17.0.1.0.0 |  | Show the delivery state on the sale order
[sale_exception](sale_exception/) | 17.0.1.0.0 |  | Custom exceptions on sale order
[sale_fixed_discount](sale_fixed_discount/) | 17.0.1.0.2 |  | Allows to apply fixed amount discounts in sales orders.
[sale_force_invoiced](sale_force_invoiced/) | 17.0.1.1.0 |  | Allows to force the invoice status of the sales order to Invoiced
[sale_invoice_policy](sale_invoice_policy/) | 17.0.1.0.0 |  | Sales Management: let the user choose the invoice policy on the order
[sale_manual_delivery](sale_manual_delivery/) | 17.0.1.0.0 |  | Create manually your deliveries
[sale_order_archive](sale_order_archive/) | 17.0.1.0.0 |  | Archive Sale Orders
[sale_order_line_menu](sale_order_line_menu/) | 17.0.1.0.0 |  | Adds a Sale Order Lines Menu
[sale_order_price_recalculation](sale_order_price_recalculation/) | 17.0.1.0.0 |  | Recalculate prices / Reset descriptions on sale order lines
[sale_order_qty_change_no_recompute](sale_order_qty_change_no_recompute/) | 17.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Prevent recompute if only quantity has changed in sale order line
[sale_order_revision](sale_order_revision/) | 17.0.1.0.0 |  | Keep track of revised quotations
[sale_order_type](sale_order_type/) | 17.0.1.0.0 |  | Sale Order Type
[sale_procurement_group_by_line](sale_procurement_group_by_line/) | 17.0.1.0.0 |  | Base module for multiple procurement group by Sale order
[sale_product_set](sale_product_set/) | 17.0.1.0.0 |  | Sale product set
[sale_shipping_info_helper](sale_shipping_info_helper/) | 17.0.1.0.0 |  | Add shipping amounts on sale order
[sale_start_end_dates](sale_start_end_dates/) | 17.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Adds start date and end date on sale order lines
[sale_stock_cancel_restriction](sale_stock_cancel_restriction/) | 17.0.1.0.0 |  | Sale Stock Cancel Restriction
[sale_stock_picking_blocking](sale_stock_picking_blocking/) | 17.0.1.1.0 |  | Allow you to block the creation of deliveries from a sale order.
[sale_stock_picking_note](sale_stock_picking_note/) | 17.0.1.0.0 | [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) [![EmilioPascual](https://github.com/EmilioPascual.png?size=30px)](https://github.com/EmilioPascual) | Add picking note in sale and purchase order
[sale_tier_validation](sale_tier_validation/) | 17.0.1.0.0 |  | Extends the functionality of Sale Orders to support a tier validation process.
[sales_team_security](sales_team_security/) | 17.0.1.0.0 | [![pedrobaeza](https://github.com/pedrobaeza.png?size=30px)](https://github.com/pedrobaeza) [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | New group for seeing only sales channel's documents

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
