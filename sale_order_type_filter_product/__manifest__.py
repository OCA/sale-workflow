# Copyright 2026 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Type Filter Product",
    "summary": "Restrict products available on sales by sale order type",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale_order_type",
    ],
    "data": [
        "views/product_template_views.xml",
        "views/product_views.xml",
        "views/sale_order_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_order_type_filter_product/static/src/js/product_configurator_dialog.esm.js",
            "sale_order_type_filter_product/static/src/js/sale_order_line_product_field.esm.js",
        ],
    },
    "installable": True,
}
