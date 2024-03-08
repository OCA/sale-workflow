# Copyright 2024 Ecosoft (<https://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sales Cost-Revenue Spread",
    "summary": "Spread costs and revenues over a custom period on sales order",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "depends": ["sale", "account_spread_cost_revenue"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_views.xml",
        "views/account_spread.xml",
        "wizards/account_spread_sale_line_link_wizard.xml",
    ],
    "installable": True,
}
