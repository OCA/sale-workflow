# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "sale_section_stock_move",
    "summary": "Sale section on stock moves",
    "version": "19.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
        "sale_order_line_section",
    ],
    "data": [
        "views/stock_picking_views.xml",
    ],
}
