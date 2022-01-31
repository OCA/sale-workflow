# Copyright 2020 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Global Discount Amount",
    "summary": "Allows to apply an amount of global discount in sale orders.",
    "version": "14.0.1.0.0",
    "category": "Sales/Sales",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": [
        "sale_management",
        "account_global_discount_amount",
    ],
    "data": [
        "views/sale.xml",
    ],
    "installable": True,
}
