# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Sale Confirmation Group",
    "summary": "Allows configuring a list of groups per-company who are granted"
    " permission to confirm sale orders",
    "version": "18.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA) ",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sale",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        # Settings view
        "wizards/res_config_settings.xml",
    ],
    "installable": True,
}
