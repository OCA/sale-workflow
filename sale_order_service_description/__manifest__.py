# Copyright 2026 NICO SOLUTIONS - ENGINEERING & IT, Nils Coenen
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Sale Order Service Description",
    "summary": "Adds a service description field on sale orders",
    "version": "19.0.1.0.0",
    "category": "Sales Management",
    "author": "NICO SOLUTIONS, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "LGPL-3",
    "depends": ["sale_management"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
