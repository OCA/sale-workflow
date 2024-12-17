# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Blanket Order Sale Margin",
    "summary": """Ensure sale margins are properly set on call off order lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_order_blanket_order",
        "sale_margin",
    ],
    "auto_install": True,
}
