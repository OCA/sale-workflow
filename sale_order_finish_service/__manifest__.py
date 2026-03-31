# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Finish Service",
    "summary": """Adds a finish service flag on sale orders""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_service"],
    "data": [
        "views/sale_order.xml",
    ],
}
