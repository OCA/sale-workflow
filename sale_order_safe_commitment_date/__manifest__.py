# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
{
    "name": "Sale order safe commitment date",
    "summary": "Avoid confirming a commitment date previous to the expected date",
    "version": "16.0.1.2.0",
    "development_status": "Alpha",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["chienandalu", "rafaelbn"],
    "license": "LGPL-3",
    "depends": ["sale"],
    "data": [
        "views/sale_order_views.xml",
    ],
}
