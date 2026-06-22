# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Sale Invoice Group",
    "summary": "Restrict creating invoices from sales orders to a dedicated"
    " security group",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sale",
    "license": "AGPL-3",
    "depends": ["sale", "account"],
    "data": [
        "security/res_groups.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
}
