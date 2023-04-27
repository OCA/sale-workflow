# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale order line price history",
    "version": "16.0.1.0.0",
    "category": "Sales Management",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/sale_order_line_price_history.xml",
        "views/sale_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_order_line_price_history/static/src/js/*.js",
            "sale_order_line_price_history/static/src/xml/*.xml",
        ],
    },
    "installable": True,
}
