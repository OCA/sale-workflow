# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Partner Pricelist",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": ["sale"],
    "data": [
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "installable": True,
}
