# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Sale By Packaging",
    "summary": "Manage sale of packaging",
    "version": "15.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_order_line_packaging_qty", "product_packaging_type"],
    "data": [
        "views/product_packaging.xml",
        "views/product_packaging_type.xml",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/sale_order_line.xml",
    ],
}
