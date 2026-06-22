# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Pricelist Fixed Price No Discount",
    "summary": """Prevents users from applying manual discounts on sale order lines
    when the price comes from a fixed-price pricelist rule.""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "data": [
        "views/sale_order_views.xml",
        "views/sale_order_line_views.xml",
    ],
    "maintainers": ["sbejaoui"],
}
