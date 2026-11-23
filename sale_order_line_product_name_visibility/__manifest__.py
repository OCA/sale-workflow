{
    "name": "Sale order line product name visibility",
    "version": "20.0.1.0.0",
    "summary": "Hide product name on sale order lines",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale",
        "account_invoice_line_product_name_visibility",
    ],
    "data": [
        "views/sale_order_line_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
