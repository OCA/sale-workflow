# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Down Payment Deduct Partial",
    "summary": "Allow to deduct down payments partially in invoices",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_management"],
    "data": [
        "wizard/sale_make_invoice_advance.xml",
    ],
    "application": False,
    "installable": True,
}
