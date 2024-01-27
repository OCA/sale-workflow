# Copyright 2023 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Loyalty Product Exclude",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Sale",
    "summary": "Exclude products from sale loyalty program",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_loyalty"],
    "data": [
        "views/product_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
