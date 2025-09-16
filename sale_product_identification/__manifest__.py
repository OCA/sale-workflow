# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Product Identification Numbers",
    "author": "Binhex,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale", "partner_identification"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "wizards/wizard_confirm_identification.xml",
    ],
}
