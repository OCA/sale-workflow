# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
{
    "name": "Sale line locking by pricelist",
    "summary": "Lock price or discount edition depending on pricelist items",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["chienandalu", "rafaelbn"],
    "license": "LGPL-3",
    "depends": [
        "sale",
        "base_view_inheritance_extension",
    ],
    "data": [
        "views/product_pricelist_views.xml",
        "views/sale_order_views.xml",
    ],
}
