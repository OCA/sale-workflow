# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Force Invoiced Quantity",
    "summary": "Add manual invoice quantity in sales order lines",
    "version": "16.0.1.0.0",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "category": "sale",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_force_invoiced"],
    "data": [
        "views/sale_order.xml",
    ],
    "demo": [
        "demo/demo_product.xml",
        "demo/demo_sale_order.xml",
    ],
    "installable": True,
}
