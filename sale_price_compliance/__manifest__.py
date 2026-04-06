# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Sale Price Compliance",
    "summary": "Visual price compliance based on product, category and company thresholds",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
    ],
    "data": [
        "security/sale_price_compliance.xml",
        "views/res_config_settings_view.xml",
        "views/product_category_view.xml",
        "views/product_template_view.xml",
        "views/product_product_view.xml",
        "views/sale_order_line_view.xml",
        "views/sale_order_view.xml",
        "report/sale_report_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "assets": {
        "web.assets_backend": [
            "sale_price_compliance/static/src/**/*",
        ],
    },
}
