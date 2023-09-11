# Copyright 2017 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Product Recommendation",
    "summary": "Recommend products to sell to customer based on history",
    "version": "13.0.2.0.5",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale"],
    "data": ["wizards/sale_order_recommendation_view.xml", "views/sale_order_view.xml"],
}
