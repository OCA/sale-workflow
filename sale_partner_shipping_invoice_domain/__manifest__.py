# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Shipping and Invoice Domain",
    "summary": """
        Adds a sensible domain to the shipping
        and invoicing addresses on sale form view""",
    "version": "14.0.1.0.2",
    "license": "AGPL-3",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_stock", "sale_commercial_partner", "web_domain_field"],
    "data": [
        "views/sale_order.xml",
    ],
    "demo": [],
}
