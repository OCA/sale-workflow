# Copyright 2025 Ethan Hildick
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Fixed Triple Discount",
    "summary": "Compatibility between fixed and triple discount modules",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_fixed_discount", "sale_triple_discount"],
    "auto_install": True,
    "data": ["views/sale_order_view.xml"],
}
