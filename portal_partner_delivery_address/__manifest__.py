# Copyright 2026 Tohid Pathan (Allied Vision Technologies Pvt. Ltd.)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Portal Partner Delivery Address",
    "version": "19.0.1.0.0",
    "summary": (
        "Enable portal customers to manage multiple delivery addresses "
        "and select their preferred shipping address on quotations."
    ),
    "category": "Sales/Sales",
    "author": "Allied Vision Technologies Pvt. Ltd., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "maintainers": ["tohid-pathan"],
    "development_status": "Beta",
    "depends": [
        "base",
        "portal",
        "sale",
    ],
    "data": [
        "security/ir_rule.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "portal_partner_delivery_address/static/src/js/portal_delivery_address.esm.js",
            "portal_partner_delivery_address/static/src/css/portal_delivery_address.css",
        ],
        "web.assets_tests": [
            "portal_partner_delivery_address/static/src/js/tour_portal_delivery_address.esm.js",
        ],
    },
    "installable": True,
    "auto_install": False,
}
