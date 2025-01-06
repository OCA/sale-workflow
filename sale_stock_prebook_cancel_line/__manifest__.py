# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Stock Prebook Cancel Line",
    "summary": """Takes into account prebook pickings into the computation
     of cancelled qty on the sale order lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_stock_prebook",
        "sale_order_line_cancel",
    ],
    "auto_install": True,
    "data": [],
    "demo": [],
}
