# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Sale Order Line Launch Stock Rule Hook",
    "summary": "Adds Hook to Sales Order Line's _action_launch_stock_rule method.",
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_stock"],
    "post_load": "post_load_hook",
}
