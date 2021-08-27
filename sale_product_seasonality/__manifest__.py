# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Product seasonality",
    "summary": "Integrates rules for products' seasonal availability with sales",
    "version": "14.0.1.1.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Others",
    "depends": [
        # core
        "sale",
        # OCA/product-attribute
        "product_seasonality",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        # Views
        "views/sale_order.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "auto_install": True,
}
