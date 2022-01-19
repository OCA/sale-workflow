# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Line Unit Price No Tax",
    "summary": """
        This module allows to display unit price with no taxes (on sale order
        lines and invoice lines) if prices are
        managed with included taxes.""",
    "maintainers": ["rousseldenis"],
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale",
    ],
    "data": ["views/sale_order.xml", "report/report_sale_order.xml"],
}
