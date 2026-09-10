# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Invoice Tree Customer Ref",
    "summary": """This module allows to display customer reference (ref) on sale order
    and invoices tree views""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale",
    ],
    "data": ["views/sale_order_view.xml", "views/account_move.xml"],
}
