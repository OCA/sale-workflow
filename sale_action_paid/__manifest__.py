# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Action Paid",
    "summary": """
        Allow to mark the payment transaction as paid
        """,
    "author": "BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": [
        "views/sale_order_views.xml",
    ],
}
