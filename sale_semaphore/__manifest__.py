# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Semaphore",
    "summary": "Adds a semaphore for commercial purposes",
    "version": "18.0.1.0.1",
    "category": "Sale",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "views/account_invoice_report_views.xml",
        "views/account_move_views.xml",
        "views/product_category_views.xml",
        "views/product_views.xml",
        "views/sale_order_views.xml",
        "views/sale_report_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "assets": {
        "web.assets_backend": [
            "sale_semaphore/static/src/semaphore/*",
        ],
    },
    "pre_init_hook": "pre_init_hook",
}
