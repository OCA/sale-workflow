# Copyright 2021 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Product Classification",
    "summary": "Classify products regarding their sales performance",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "sale",
    ],
    "data": [
        "views/product_template_views.xml",
        "views/res_config_settings_views.xml",
        "data/ir_cron.xml",
    ]
}
