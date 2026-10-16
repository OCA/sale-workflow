# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Sale Commitment Date Required On Confirm",
    "summary": "Require the delivery date to confirm a sales order and show it"
    " in the order header",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "views/res_config_settings.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
