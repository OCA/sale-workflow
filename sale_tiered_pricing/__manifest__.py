# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Tiered Pricing",
    "summary": """
        Tiered pricing can be defined and used in pricelists.
        """,
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://acsone.eu",
    "depends": ["sale_management"],  # pricelist settings are there...
    "data": [
        "security/groups.xml",
        "views/pricelist.xml",
        "wizard/tiered_pricing_wizard.xml",
        "views/product.xml",
        "views/partner.xml",
    ],
    "demo": ["demo/tiered_pricing.xml", "demo/product_template.xml"],
    "pre_init_hook": "pre_init_hook",
}
