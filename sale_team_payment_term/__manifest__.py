# Copyright 2022 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Team Payment Term",
    "summary": "add payment term on sale team",
    "version": "14.0.1.0.0",
    "category": "sale-workflow",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
        "account",
        "sales_team",
    ],
    "data": [
        "views/crm_team.xml",
    ],
}
