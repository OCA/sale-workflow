# Copyright 2024 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Stock Qty By Warehouse",
    "summary": "Display the stock quantity by warehouse on sale order lines",
    "version": "18.0.1.0.0",
    "category": "Hidden",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "ACSONE SA/NV, Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/res_config_settings.xml",
        "views/sale_order.xml",
        "views/stock_warehouse.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_stock_qty_by_warehouse/static/src/widgets/qty_by_warehouse_widget.esm.js",
            "sale_stock_qty_by_warehouse/static/src/widgets/qty_by_warehouse_widget.xml",
        ],
    },
}
