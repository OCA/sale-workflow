# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Sale Block no Stock",
    "summary": "Block Sales if products has not enough Quantity based on a chosen field",
    "version": "16.0.2.0.0",
    "development_status": "Alpha",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_stock", "mail_message_destiny_link_template"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "wizard/sale_order_block_wizard_views.xml",
    ],
}
