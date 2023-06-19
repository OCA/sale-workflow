# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Form Sale Link",
    "summary": """
        Adds a button on product forms to access Sale Lines""",
    "version": "15.0.1.0.1",
    "license": "AGPL-3",
    "category": "Sales",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "data": [
        "views/sale_order_line.xml",
        "views/product_product.xml",
        "views/product_template.xml",
    ],
}
