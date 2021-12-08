# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Option Product Group",
    "summary": """
        Adds a group and configuration entry to hide/show optional products in sale orders""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_management",
    ],
    "data": [
        "security/security.xml",
        "views/sale_order.xml",
        "views/res_config_settings.xml",
    ],
}
