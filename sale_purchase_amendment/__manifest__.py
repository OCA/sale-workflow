# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Purchase Amendment",
    "summary": """
        Allows to amend purchase generated from sale order lines""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_procurement_amendment",
        "sale_order_line_chained_move_purchase",
        "purchase_stock",
    ],
}
