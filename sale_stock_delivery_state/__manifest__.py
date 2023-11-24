# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Stock Delivery State",
    "summary": "Change the way to compute the delivery state",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/sale-workflow",
    "author": " Akretion,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_stock",
        "sale_delivery_state",
    ],
    "auto_install": True,
    "data": ["views/sale_order_views.xml"],
    "demo": [],
    "post_init_hook": "post_init_hook",
}
