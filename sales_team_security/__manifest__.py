# Copyright 2016-2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sales documents permissions by channels (teams)",
    "summary": "New group for seeing only sales channel's documents",
    "version": "13.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "development_status": "Production/Stable",
    "maintainers": ["pedrobaeza"],
    "depends": ["crm", "sale"],
    "data": ["security/sales_team_security.xml", "views/res_partner_view.xml"],
    "post_init_hook": "post_init_hook",
}
