# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Sale Exception Product Manufactured for Customer",
    "summary": "The partner set in the sales order can order only if he/she "
               "has a commercial entity that is listed as one of the partners "
               "for which the products can be manufactured for.",
    "version": "13.0.1.0.0",
    "category": "Sales",
    "website": "https://www.camptocamp.com",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "data": [
        "data/exception_rule.xml",
    ],
    "demo": [
        "demo/exception_rule.xml",
    ],
    "depends": [
        "sale_exception",
        "product_sale_manufactured_for",
    ],
}
