# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Sell Only By Packaging",
    "summary": "Manage sale of packaging",
    "version": "19.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, BCIM, Niboo, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale", "uom"],
    "data": [
        "views/uom_uom.xml",
        "views/product_template.xml",
        "views/product_product.xml",
    ],
}
