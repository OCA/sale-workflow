# Copyright 2019 Akretion (<http://www.akretion.com>)
# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale order restricted quantity: min, max, multiple-of",
    "version": "17.0.1.0.0",
    "category": "Sales Management",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_management"],
    "data": [
        "views/product_category_views.xml",
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
