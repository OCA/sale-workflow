# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "Sale auto remove zero quantity lines",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "summary": "On sale confirmation remove lines with zero quantities",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "category": "Sales/Sales",
    "data": [
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
}
