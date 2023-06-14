# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Line Chained Move Purchase",
    "summary": """
        Allows to get sale related line on purchase order line level""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "maintainers": ["rousseldenis"],
    "depends": ["sale_order_line_chained_move", "purchase_stock"],
    "post_init_hook": "post_init_hook",
}
