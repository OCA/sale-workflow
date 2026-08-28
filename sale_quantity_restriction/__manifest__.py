# Copyright 2025 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Quantity Restriction",
    "version": "17.0.1.0.0",
    "summary": "Restricts sale order line quantities based on min, max or multiple",
    "category": "Sales Management",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/restriction_views.xml",
        "views/product_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
