# Copyright 2025 APSL Nagarro
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Compute Commitment Date",
    "version": "18.0.1.0.0",
    "category": "Sales Management",
    "summary": "Automatically computes the commitment date based on product"
    "lead times and attributes",
    "author": "APSL - Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["mpascuall"],
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_management", "stock"],
    "data": [
        "views/product_attribute_value.xml",
        "views/product_template.xml",
    ],
    "installable": True,
    "application": False,
}
