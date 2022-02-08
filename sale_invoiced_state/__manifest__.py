# Copyright 2022 PyTech SRL - Alessandro Uffreduzzi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Invoiced State",
    "summary": "Shows if the Sales Order has been invoiced",
    "version": "12.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "PyTech SRL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "demo": [
        "demo/sale_demo.xml",
    ],
}
