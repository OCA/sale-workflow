# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Stock Order Line Quantity Readonly",
    "summary": "Restrict Sale Order Line Quantity Editable",
    "version": "16.0.1.0.0",
    "category": "Sale",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_stock", "base_view_inheritance_extension"],
    "data": ["views/sale_order_view.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
