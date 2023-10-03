# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Sale Invoice Frequency",
    "summary": "Define the invoice frequency for customers",
    "version": "15.0.1.1.1",
    "development_status": "Beta",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "yajo", "EmilioPascual"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sale_invoice_frequency_data.xml",
        "views/sale_invoice_frequency_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
    ],
}
