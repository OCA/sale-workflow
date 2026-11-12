# Copyright 2026 M. Salman
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Cancelled Sale Order Hide",
    "summary": "Hide cancelled sale orders, and the invoices/credit notes "
    "linked to them, from the default list views",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "M. Salman, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "development_status": "Beta",
    "maintainers": ["your-github-username"],
    "depends": [
        "sale",
        "account",
    ],
    "data": [
        "views/sale_order_action.xml",
        "views/account_move_action.xml",
    ],
}
