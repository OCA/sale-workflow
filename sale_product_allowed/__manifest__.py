# Copyright 2021 - 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Product Allowed",
    "summary": "Integrates rules for products allowed with sales",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Others",
    "depends": [
        # core
        "sale",
        # OCA/product-attribute
        "product_allowed_list",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        # Views
        "views/sale_order.xml",
        "views/menu.xml",
        # Security
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "auto_install": True,
}
