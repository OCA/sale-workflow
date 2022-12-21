# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Order Product Assortment Availability Inline",
    "summary": "Glue module to display stock available when an assortment is defined "
    "for a partner",
    "version": "13.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Sergio-teruel"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "sale_order_product_assortment",
        "sale_order_product_availability_inline",
    ],
    "data": ["views/sale_order_view.xml"],
    "auto_install": True,
}
