# Copyright 2023 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Currency Rate in Sale Order",
    "version": "16.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": ["sale"],
    "data": [
        "data/decimal_precision_data.xml",
        "views/sale_order.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
}
