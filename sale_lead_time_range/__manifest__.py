# Copyright 2024 ForgeFlow S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Lead Time Range - Sale",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "license": "AGPL-3",
    "depends": ["sale_stock"],
    "data": [
        "views/product_views.xml",
        "views/sale_order_line.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
