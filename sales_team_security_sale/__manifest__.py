# Copyright 2020 Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale documents permissions by teams",
    "summary": "Integrates sales_team_security with sale",
    "version": "14.0.3.0.1",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Iván Todorovich, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "development_status": "Production/Stable",
    "maintainers": ["ivantodorovich"],
    "depends": ["sale", "sales_team_security"],
    "data": ["security/security.xml"],
    "auto_install": True,
}
