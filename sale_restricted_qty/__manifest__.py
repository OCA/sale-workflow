# Copyright 2019 Akretion (<http://www.akretion.com>)
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale order min quantity",
    "version": "16.0.1.0.0",
    "category": "Sales Management",
    "author": "Akretion, Odoo Community Association (OCA)",
    "contributors": ["Ashish Hirpara"],
    "maintainers": ["ashishhirapara"],
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_management"],
    "data": [
        "views/product_category_views.xml",
        "views/product_template_views.xml",
        "views/product_product_views.xml",
        "views/sale_views.xml",
    ],
    "installable": True,
}
