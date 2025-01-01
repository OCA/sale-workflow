# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Sale Order Line all Product Attribute Values",
    "summary": "Store Product Attribute Values in Sale Order Lines",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_order_line_view.xml",
    ],
}
