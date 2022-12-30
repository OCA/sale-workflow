# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Coupon Product Management",
    "summary": "Improves related product management via sale coupons",
    "version": "13.0.1.0.1",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_coupon"],
    "data": [
        "views/product_category_views.xml",
        "views/product_product_views.xml",
        "views/sale_coupon_program_views.xml",
    ],
    "installable": True,
}
