# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Pricelist Fixed Price No Triple Discount",
    "summary": "Prevent triple discounts on sale lines using fixed-price pricelist "
    "rules",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_pricelist_fixed_price_no_discount", "sale_triple_discount"],
    "data": ["views/sale_order_views.xml"],
    "maintainers": ["sbejaoui"],
}
