# © 2016 Sylvain Van Hoof
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Order Line Cancel",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, ACSONE SA/NV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Sales",
    "summary": """Sale cancel remaining""",
    "depends": ["sale_stock"],
    "data": [
        "security/sale_order_line_cancel.xml",
        "wizards/sale_order_line_cancel.xml",
        "views/sale_order.xml",
        "views/sale_order_line.xml",
    ],
    "website": "https://github.com/OCA/sale-workflow",
}
