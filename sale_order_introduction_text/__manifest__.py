{
    "name": "Sale Order Introduction Text",
    "version": "16.0.1.0.0",
    "summary": (
        "Add introduction text to sale orders, sale order reports, "
        "and customer portal."
    ),
    "author": "BizzAppDev Systems Pvt. Ltd.,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "LGPL-3",
    "category": "Sales",
    "depends": ["sale_management"],
    "data": [
        "views/res_config_setting_views.xml",
        "views/sale_order_views.xml",
        "report/sale_order_report.xml",
    ],
    "installable": True,
}
