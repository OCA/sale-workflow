# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Cancel Confirmed Invoice",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow," "Odoo Community Association (OCA)",
    "category": "Sale",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_management"],
    "data": [
        "wizards/sale_order_cancel_view.xml",
        "views/res_config_settings_views.xml",
    ],
    "auto_install": False,
    "installable": True,
}
