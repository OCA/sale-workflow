# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sales Team Territory",
    "summary": "Assign sales team and salesperson to partners by country or state",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "development_status": "Beta",
    "depends": ["sales_team"],
    "data": [
        "views/crm_team_views.xml",
        "views/res_partner_views.xml",
    ],
}
