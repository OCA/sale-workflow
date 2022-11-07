# Copyright 2021 - 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Product Allowed Dates",
    "summary": "Integrates rules for products' date availability with sales",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Others",
    "depends": [
        # OCA/product-attribute
        "product_allowed_list_date",
        # OCA/sale-workflow
        "sale_product_allowed",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        # Views
        "views/sale_order.xml",
    ],
    "installable": True,
    "auto_install": True,
}
