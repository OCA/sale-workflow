# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Product Manufactured for Customer",
    "summary": "Allows to indicate in products that they were made "
    "specifically for some customers.",
    "version": "15.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "data": [
        "views/product_template.xml",
        "views/sale_order.xml",
    ],
    "depends": [
        "product",
        "sale",
        "sale_commercial_partner",
    ],
}
