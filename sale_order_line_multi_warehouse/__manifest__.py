# Copyright 2021 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Line Multi Warehouse",
    "summary": "Sale Order Line Multi Warehouse",
    "version": "16.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_warehouse_views.xml",
        "views/sale_order_line_warehouse_views.xml",
        "views/sale_order_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/so_multi_warehouse_change_wizard_views.xml",
    ],
}
