# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Sale Stock Readonly",
    "summary": "Read-only access to the deliveries of sales orders",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["sebalix"],
    "license": "LGPL-3",
    "depends": [
        # odoo
        "sale_stock",
        # OCA/sale-workflow
        "sale_readonly",
        # OCA/stock-logistics-workflow
        "stock_readonly",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "auto_install": True,
    "installable": True,
}
