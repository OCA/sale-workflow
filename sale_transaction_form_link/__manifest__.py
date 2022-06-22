# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Transaction Form Link",
    "summary": """
        Allows to display a link to payment transactions on Sale Order form view.""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "maintainers": ["rousseldenis"],
    "depends": [
        "payment",
        "sale",
    ],
    "data": [
        "views/sale_order.xml",
    ],
    "demo": [
        "demo/payment_transaction.xml",
    ],
}
