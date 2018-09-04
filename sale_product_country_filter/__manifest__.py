# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Product Country Filter",
    "summary": """
        Prevent products from being sold in certain countries""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow/",
    "depends": [
        "sale"
    ],
    "data": [
        "views/product_category.xml",
        "views/product_product.xml",
        "views/product_template.xml",
        "views/sale_config_settings.xml",
    ],
}
