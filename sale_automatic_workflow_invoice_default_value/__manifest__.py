# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale automatic workflow invoice default values",
    "version": "14.0.1.0.0",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Sale",
    "depends": [
        # oca/sale-workflow
        "sale_automatic_workflow",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/sale_workflow_process.xml",
    ],
}
