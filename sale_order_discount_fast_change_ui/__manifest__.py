# Copyright 2023 Akretion - Florian Mounier
{
    "name": "Sale Order Disount Fast Change UI",
    "summary": "This module disables the slow odoo discount change wizard "
    "interface and replaces it with a non transactional faster one",
    "version": "14.0.1.0.1",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "wizard/sale_order_discount_fast_change.xml",
        "views/assets.xml",
        "views/sale_order_view.xml",
    ],
}
