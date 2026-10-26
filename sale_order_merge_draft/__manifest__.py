# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Sale Order Merge Draft",
    "summary": """Merge Sale Orders in state draft/sent""",
    "category": "Sales",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale",
    ],
    "data": [
        "data/ir_actions_server.xml",
    ],
    "installable": True,
}
