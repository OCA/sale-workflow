# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Payment Terms From Invoice Address",
    "summary": """Adds a config option to make the payment terms
    on sale orders computed based on the "invoice address"
    (`partner_invoice_id`) instead of the "customer" (`partner_id`).""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_management"],
    "data": [
        "views/res_config_setting.xml",
    ],
}
