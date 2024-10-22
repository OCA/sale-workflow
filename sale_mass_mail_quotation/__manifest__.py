# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Mass Mail Quotation",
    "summary": """
        Mass mail quotations""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "data": ["wizards/quotation_mass_mail_wizard.xml", "security/ir.model.access.csv"],
    "mainainers": ["kevinkhao", "bealdav"],
    "demo": [],
}
