# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Product Documentation Set",
    "summary": """
        Send out Product Documentation along with Sale Orders""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale", "product_documentation_set"],  # from OCA/product-attribute
    "data": [
        'views/sale_order.xml',
    ],
    "auto_install": True,
}
