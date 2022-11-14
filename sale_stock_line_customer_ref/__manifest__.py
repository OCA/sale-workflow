# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Sale Stock Line Customer Reference",
    "summary": (
        "Allow you to add a customer reference on order lines "
        "propagaged to move operations."
    ),
    "version": "14.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["sebalix"],
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales/Sales",
    "depends": ["sale_stock"],
    "data": [
        "views/sale_order.xml",
        "views/stock_picking.xml",
        "views/stock_move.xml",
        "views/stock_move_line.xml",
        "views/stock_package_level.xml",
        "views/stock_quant_package.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "development_status": "Beta",
    "pre_init_hook": "pre_init_hook",
}
