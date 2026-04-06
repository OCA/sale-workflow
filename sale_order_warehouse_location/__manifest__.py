# Copyright 2025 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Warehouse Location",
    "summary": "Set warehouse in sales orders based on delivery country/state.",
    "version": "16.0.1.0.0",
    "category": "Stock",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/stock_warehouse_views.xml",
    ],
}
