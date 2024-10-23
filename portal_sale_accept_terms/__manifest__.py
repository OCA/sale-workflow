#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Portal Sale accept Terms",
    "version": "16.0.1.0.0",
    "category": "Sale",
    "author": "Aion Tech, Odoo Community Association (OCA)",
    "maintainers": [
        "SirAionTech",
    ],
    "website": "https://github.com/OCA/sale-workflow"
    "/tree/16.0/portal_sale_accept_terms",
    "license": "AGPL-3",
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_order_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "portal_sale_accept_terms/static/src/js/accept_terms.js",
        ],
        "web.assets_tests": [
            "portal_sale_accept_terms/static/tests/tours/accept_terms.esm.js",
        ],
    },
}
