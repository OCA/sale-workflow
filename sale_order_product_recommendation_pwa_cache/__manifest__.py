# Copyright 2021 Tecnativa - David Vidal
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale PWA Cache Product Recommendation",
    "summary": "Glue module to show the product recommendation button",
    "version": "12.0.1.0.0",
    "development_status": "Beta",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["chienandalu"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "sale_pwa_cache",
        "sale_order_product_recommendation",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
}
