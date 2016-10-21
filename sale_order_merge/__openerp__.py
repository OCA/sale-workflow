# coding: utf-8
# Copyright 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Merge sale orders",
    "summary": "Merge sale orders that are confirmed, invoiced or delivered",
    "version": "8.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/oca/sale-workflow",
    "author": "Opener B.V., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/sale_order.xml",
        "views/sale_order_merge.xml",
    ],
}
