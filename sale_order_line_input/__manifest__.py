# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Line Input",
    "summary": "Search, create or modify directly sale order lines",
    "version": "16.0.1.0.1",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_management"],
    "data": [
        "security/sale_order_line_view_group.xml",
        "views/sale_order_line_view.xml",
        "views/sale_order_view.xml",
        "views/res_config_settings.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_order_line_input/static/src/**/*",
        ],
    },
}
