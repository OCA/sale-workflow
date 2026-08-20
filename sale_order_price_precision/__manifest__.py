# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Price Precision",
    "summary": "Add decimal precision for sale order and invoice prices",
    "version": "17.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": [
        "sale",
        "account",
    ],
    "data": [
        "data/decimal_precision_data.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
    "development_status": "Beta",
}
