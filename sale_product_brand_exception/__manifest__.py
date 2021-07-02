# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale product brand exception",
    "summary": "Define rules for sale order and brands",
    "version": "14.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Sale",
    "depends": [
        "product_brand",
        "sale_exception",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        "data/exception_rule.xml",
        "views/product_brand_view.xml",
    ],
    "demo": [
        "demo/exception_rule.xml",
    ],
    "installable": True,
}
