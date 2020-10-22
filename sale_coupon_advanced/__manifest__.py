# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Coupon Advanced Programs",
    "summary": "Extend coupon program features",
    "version": "13.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_coupon"],
    "data": [
        "views/product_pricelist_views.xml",
        "views/sale_coupon_program_views.xml",
        "wizard/sale_coupon_generate_views.xml",
    ],
    "installable": True,
}
