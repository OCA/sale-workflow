# Copyright 2026 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Stock Put-to-Order",
    "summary": "Sale-order-aware put-to-order zone configuration"
    " and target location resolution.",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        # Odoo Community
        "sale_stock",
    ],
    "data": [
        "views/stock_location_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
