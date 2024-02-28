# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Validity Auto-Cancel",
    "version": "15.0.1.0.0",
    "category": "Sales",
    "license": "LGPL-3",
    "summary": "Automatically cancel quotations after validity period.",
    "depends": ["sale_management"],
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "data": ["data/ir_cron.xml", "views/res_config_settings.xml"],
    "installable": True,
    "maintainers": ["JordiMForgeFlow"],
}
