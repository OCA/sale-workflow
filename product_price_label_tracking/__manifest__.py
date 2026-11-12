# Copyright 2026 arielbarreiros96
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product Price Label Tracking",
    "version": "19.0.1.0.0",
    "summary": "Track which product labels must be reprinted after price changes",
    "author": "arielbarreiros96, Odoo Community Association (OCA)",
    "maintainers": ["arielbarreiros96"],
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": ["sale_stock"],
    "data": [
        "security/product_price_label_tracking_security.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/product_label_track_views.xml",
        "views/product_label_tracking_rule_views.xml",
        "wizards/product_label_layout_views.xml",
    ],
    "installable": True,
}
