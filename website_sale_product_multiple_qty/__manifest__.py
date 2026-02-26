# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Website Sale Product Multiple Qty",
    "summary": "Allows setting a multiple quantity for products on the website.",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        # Odoo/core
        "website_sale",
        # OCA/sale-workflow
        "sale_product_multiple_qty",
    ],
    "maintainers": ["yankinmax"],
    "data": [
        # Views
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "website_sale_product_multiple_qty/static/src/js/product/**/*",
            "website_sale_product_multiple_qty/static/src/js/quantity_buttons/**/*",
        ],
        "web.assets_frontend": [
            "website_sale_product_multiple_qty/static/src/js/interactions/**/*",
        ],
    },
}
