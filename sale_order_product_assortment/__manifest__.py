# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Sale Order Product Assortment",
    "summary": "Module that allows to use the assortments on sale orders",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["CarlosRoca13"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale", "product_assortment"],
    "data": ["views/sale_order_view.xml"],
}
