# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Default packaging for sales",
    "summary": "Set a default product packaging and simplify its usage in sales orders",
    "version": "16.0.1.1.0",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["yajo"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale"],
    "data": [
        "views/product_packaging_view.xml",
        "views/sale_order_view.xml",
    ],
}
