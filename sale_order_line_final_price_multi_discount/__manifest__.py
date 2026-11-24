# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Line Final Price - Multi Discount",
    "summary": "Glue between sale_order_line_final_price and "
    "sale_multi_discount: the final price drives the discount distribution",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        "sale_order_line_final_price",
        "sale_multi_discount",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
