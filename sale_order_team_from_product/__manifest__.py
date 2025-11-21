# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Team from Product",
    "summary": "Set Sales Team on quotations from product Sales Teams",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        "sale_management",
        "product_sale_team",
    ],
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "demo": [
        "demo/sale_order_demo.xml",
    ],
    "installable": True,
}
