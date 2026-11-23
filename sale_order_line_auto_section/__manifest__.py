# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Order Line Auto Section",
    "summary": "Automatically organize sale order lines into sections by "
    "product category",
    "version": "17.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "LGPL-3",
    "depends": ["sale"],
    "data": [
        "views/product_category_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
