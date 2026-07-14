# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Line Final Price",
    "summary": "Set the final price of a sale order line, and lock its unit "
    "price and discount for non sales managers",
    "version": "18.0.1.0.0",
    "category": "Sales Management",
    "author": "Tecnativa,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "maintainers": ["eduezerouali-tecnativa"],
    "installable": True,
}
