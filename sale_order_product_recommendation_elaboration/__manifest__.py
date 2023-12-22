# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Sale order product recommendation with elaborations",
    "summary": (
        "Include elaborations when generating or accepting sale order "
        "product recommendations"
    ),
    "version": "16.0.1.0.2",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["rafaelbn", "yajo"],
    "license": "AGPL-3",
    "depends": [
        "sale_order_product_recommendation",
        "sale_elaboration",
    ],
    "data": [
        "wizards/sale_order_recommendation_view.xml",
    ],
}
