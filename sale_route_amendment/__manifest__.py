# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Route Amendment",
    "summary": """
        Allows to update stock route on order lines after confirmation""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "maintainers": ["rousseldenis"],
    "depends": ["sale_stock", "sale_procurement_amendment"],
    "data": [
        "security/security.xml",
        "wizards/sale_order_line_route_amend.xml",
        "views/sale_order.xml",
    ],
}
