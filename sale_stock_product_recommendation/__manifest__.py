# Copyright 2024 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Sale Order Product Recommendation Stock",
    "summary": "Display stock info when recommending products to sell",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["yajo", "rafaelbn"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["sale_stock", "sale_order_product_recommendation"],
    "data": [
        "wizards/sale_order_recommendation_view.xml",
    ],
}
