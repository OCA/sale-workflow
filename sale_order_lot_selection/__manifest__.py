{
    "name": "Sale Order Lot Selection",
    "version": "19.0.1.0.0",
    "category": "Sales Management",
    "author": "Odoo Community Association (OCA), Agile Business Group",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_stock", "stock_restrict_lot"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/sale_order_views.xml",
        "views/report_sale_order.xml",
        "views/sale_portal_templates.xml",
        "reports/sale_report_views.xml",
    ],
    "demo": ["demo/sale_demo.xml"],
    "maintainers": ["bodedra"],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "sale_order_lot_selection/static/src/**/*",
        ],
    },
}
