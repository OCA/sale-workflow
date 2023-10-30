# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Product Recommendation",
    "summary": "Recommend products to sell to customer based on history",
    "version": "15.0.1.2.2",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/sale_order_recommendation_view.xml",
        "views/res_config_settings_views.xml",
        "views/sale_order_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_order_product_recommendation/static/src/js/units_included_widget.js",
            "sale_order_product_recommendation/static/src/css/units_included_widget.scss",
        ],
        "web.assets_qweb": [
            "sale_order_product_recommendation/static/src/xml/units_included_widget.xml",
        ],
    },
}
