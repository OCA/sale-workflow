# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale order priority",
    "summary": "Define priority on sale orders",
    "version": "12.0.1.0.2",
    "category": "Sale Workflow",
    "website": "https://github.com/OCA/sale-workflow"
               "sale_order_priority",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock"
    ],
    "data": [
        "views/sale.xml"
    ]
}
