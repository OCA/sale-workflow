# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

{
    "name": "Sale Readonly",
    "summary": "Read-only access to Sales documents",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": [
        # odoo
        "sale",
        # OCA/crm
        "sales_team_readonly",
    ],
    "data": [
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "views/sale_menus.xml",
    ],
    "installable": True,
}
