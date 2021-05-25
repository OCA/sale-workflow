# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Change Analytic Account",
    "summary": """
        This addon allow user to update analytic account on sale orders and
        related journal entries.""",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "security/sale_order_change_analytic.xml",
        "views/sale_order.xml",
        "wizards/sale_order_change_analytic.xml",
    ],
}
