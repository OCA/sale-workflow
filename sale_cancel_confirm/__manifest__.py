# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sales Cancel Confirm",
    "version": "18.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "category": "Usability",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["base_cancel_confirm", "sale"],
    "data": [
        "views/res_config_settings_views.xml",
        "wizard/sale_order_cancel_views.xml",
    ],
    "auto_install": False,
    "installable": True,
    "maintainers": ["kittiu"],
}
