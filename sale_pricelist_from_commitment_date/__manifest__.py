# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Pricelist From Commitment Date",
    "summary": "Use sale order commitment date to compute line price from pricelist",
    "version": "18.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/sale_order_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_pricelist_from_commitment_date/static/src/js/sale_product_field.esm.js",
        ],
        "web.assets_unit_tests": [
            "sale_pricelist_from_commitment_date/static/src/js/sale_product_field.esm.js",
            "sale_pricelist_from_commitment_date/static/tests/**/*",
        ],
    },
    "installable": True,
}
