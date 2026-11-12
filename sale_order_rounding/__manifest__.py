# Copyright 2026 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale Order Rounding",
    "summary": "Round up the sale order total to the nearest integer",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale"],
    "data": [
        "data/sale_order_rounding_product.xml",
        "views/sale_order_views.xml",
    ],
}
