# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Amount to Invoice",
    "version": "16.0.1.0.0",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Show total amount to invoice in quotations/sales orders ",
    "depends": [
        "sale",
        "account",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
