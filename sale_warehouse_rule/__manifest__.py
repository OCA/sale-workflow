# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Warehouse Rule",
    "version": "14.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale_stock",
        "product_attribute_value_dependant_mixin",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
}
