# Copyright 2022 Tecnativa - Sergio Teruel
# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Product Recommendation Supplierinfo",
    "summary": "Get recommendations from product supplierinfo records",
    "version": "15.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_order_product_recommendation", "purchase"],
    "data": [
        "views/product_views.xml",
        "views/sale_order_views.xml",
        "wizards/sale_order_recommendation_view.xml",
    ],
    "development_status": "Beta",
    "assets": {
        "web.assets_backend": [
            "sale_order_product_recommendation_supplierinfo/static/src/js/"
            "sale_order_product_recommendation_widget.js",
        ],
    },
}
