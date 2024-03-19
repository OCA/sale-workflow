# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Sale Order Product Recommendation with Default Packaging",
    "summary": "Quickly add recommended products to sale order by packagings",
    "version": "16.0.3.0.0",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["rafaelbn", "yajo"],
    "license": "AGPL-3",
    "auto_install": True,
    "depends": [
        "sale_order_product_recommendation",
        "sale_packaging_default",
        "web_widget_numeric_step",
    ],
    "data": [
        "wizards/sale_order_recommendation_view.xml",
    ],
}
