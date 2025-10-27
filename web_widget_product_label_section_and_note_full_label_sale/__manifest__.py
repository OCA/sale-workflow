# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

{
    "name": "Web Widget Product Label Section And Note Full Label Sale",
    "summary": """Glue module between
    web_widget_product_label_section_and_note_full_label and sale.""",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale", "web_widget_product_label_section_and_note_full_label"],
    "assets": {
        "web.assets_backend": [
            "web_widget_product_label_section_and_note_full_label_sale/static/src/**/*.js",
            "web_widget_product_label_section_and_note_full_label_sale/static/src/**/*.xml",
        ],
    },
    "application": False,
    "installable": True,
}
