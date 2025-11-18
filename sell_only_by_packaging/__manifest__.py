# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Sell Only By Packaging",
    "summary": "Manage sale of packaging",
    "version": "18.0.1.1.0",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["product_packaging_level_salable"],
    "data": [
        "views/product_packaging.xml",
        "views/product_template.xml",
        "views/product_product.xml",
    ],
}
