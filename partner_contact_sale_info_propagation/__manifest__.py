# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Partner contact sale info propagation",
    "summary": "Propagate Salesperson and Sales Channel " "from Company to Contacts",
    "version": "16.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sales_team"],
    "data": ["views/res_partner_view.xml"],
}
