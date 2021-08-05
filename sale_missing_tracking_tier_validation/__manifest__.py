# Copyright 2021 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Tier Validation",
    "summary": "Extends the functionality of Sale missing cart tracking exceptions to "
    "support a tier validation process.",
    "version": "13.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_missing_cart_tracking", "base_tier_validation"],
    "data": ["views/sale_missing_cart_tracking_exception_view.xml"],
}
