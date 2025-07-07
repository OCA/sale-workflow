# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Line Stock Moves History",
    "version": "18.0.1.0.0",
    "summary": "Show stock moves history for sale order lines",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["ppyczko"],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": ["sale_management", "sale_stock"],
    "data": ["views/sale_order_views.xml", "views/stock_move_views.xml"],
}
