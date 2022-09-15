# Copyright 2022 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Stock Picking Delivery Block",
    "summary": "Block delivery orders when sale order is blocked",
    "version": "15.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Italo LOPES, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_view.xml",
        "views/stock_picking_view.xml",
        "wizard/release_delivery_wizard.xml",
    ],
    "installable": True,
}
