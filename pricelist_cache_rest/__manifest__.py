# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Pricelist Cache Rest",
    "summary": "Provides an endpoint to get product prices for a given customer",
    "version": "15.0.1.0.0",
    "category": "Hidden",
    "author": "Odoo Community Association (OCA), Camptocamp",
    "license": "AGPL-3",
    "depends": [
        "auth_api_key",
        "base_jsonify",
        "pricelist_cache",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "installable": True,
    "data": [
        "data/ir_exports_data.xml",
        "wizards/res_config_settings.xml",
    ],
    "demo": ["demo/auth_api_key_demo.xml"],
}
