{
    "name": "Sale Delivery Request",
    "summary": "Delivery date request workflow between Sales and Planning",
    "category": "Sales/Sales",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_delivery_split_date",
        "resource",
    ],
    "data": [
        "security/sale_delivery_request_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ir_cron_data.xml",
        "wizards/sale_delivery_request_split_qty_views.xml",
        "views/sale_delivery_request_views.xml",
        "views/sale_order_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
