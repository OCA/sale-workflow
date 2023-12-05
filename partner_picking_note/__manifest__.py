# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Partner Picking Note",
    "summary": "Add picking note in partner to assign them in sale orders",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory/Delivery",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock_picking_note",
    ],
    "data": [
        "views/res_partner_view.xml",
    ],
}
