# Copyright 2019 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Product Recommendation Secondary Unit",
    "summary": "Add secondary unit to recommend products wizard",
    "version": "15.0.1.2.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": ["sale_order_product_recommendation", "sale_order_secondary_unit"],
    "data": ["wizards/sale_order_recommendation_view.xml"],
}
