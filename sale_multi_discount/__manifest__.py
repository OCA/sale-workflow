# Copyright 2026 Innovyou
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale Multi Discount",
    "summary": "Bring the multi-discount distribution from "
    "account_multi_discount to sale order lines and propagate "
    "it to invoice lines on invoicing.",
    "version": "18.0.1.0.0",
    "category": "Sales/Sales",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "maintainers": ["LorenzoC0"],
    "website": "https://github.com/OCA/sale-workflow",
    "license": "LGPL-3",
    "depends": [
        "sale",
        "account_multi_discount",
    ],
    "data": [
        "views/sale_order_views.xml",
        "report/sale_order_report.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
