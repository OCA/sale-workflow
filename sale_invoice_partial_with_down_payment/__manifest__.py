# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Invoice Partial With Down Payment",
    "summary": """Offer proportional or fixed down
        payment deduction on partial delivery invoices
        instead of a credit note.""",
    "version": "18.0.1.0.0",
    "category": "sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "data": [
        "wizard/sale_make_invoice_advance.xml",
    ],
}
