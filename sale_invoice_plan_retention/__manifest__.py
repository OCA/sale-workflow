# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Sale Invoice Plan - Retention",
    "summary": "Add to sale invoice plan, the retention on each invoice",
    "version": "15.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Purchase",
    "depends": ["sale_invoice_plan", "account_invoice_payment_retention"],
    "data": [
        "views/sale_view.xml",
    ],
    "installable": True,
    "auto_install": True,
    "maintainers": ["Saran440"],
    "development_status": "Alpha",
}
