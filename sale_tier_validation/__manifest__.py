# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Tier Validation",
    "summary": "Extends the functionality of Sale Orders to "
    "support a tier validation process.",
    "version": "13.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale", "base_tier_validation"],
    "data": ["views/sale_order_view.xml"],
}
