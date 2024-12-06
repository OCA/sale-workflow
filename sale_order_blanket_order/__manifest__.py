# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Blanket Order",
    "summary": """Manage blanket order and call of ordr""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,BCIM,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_manual_delivery",
    ],
    "excludes": ["sale_blanket_order"],
    "data": [
        "views/sale_order.xml",
        "views/sale_order_line.xml",
        "views/res_config_settings.xml",
        "data/ir_cron.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
}
