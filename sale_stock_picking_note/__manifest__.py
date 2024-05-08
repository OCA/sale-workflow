# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Stock Picking Note",
    "summary": "Add picking note in sale and purchase order",
    "version": "17.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["carlosdauden", "victoralmau", "chienandalu", "EmilioPascual"],
    "license": "AGPL-3",
    "depends": ["sale_stock"],
    "data": [
        "views/sale_order_view.xml",
        "views/stock_picking_view.xml",
        "views/report_deliveryslip.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
}
