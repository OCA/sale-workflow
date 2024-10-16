# Copyright 2024 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Blanket Orders Tier Validation",
    "summary": """
        Extends the functionality of your Sale Blanket Orders
        to support a tier validation process.
        """,
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "category": "Sales",
    "version": "17.0.1.0.0",
    "depends": [
        "sale_blanket_order",
        "base_tier_validation",
    ],
    "data": [
        "views/sale_blanket_order_views.xml",
    ],
    "application": False,
    "installable": True,
}
