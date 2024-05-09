# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Product Recommendation Quick Add",
    "summary": "Add recommended products to sale order in a single click",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_order_product_recommendation",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
}
