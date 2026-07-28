# Copyright 2023 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Sale Automatic Workflow Auto Assign",
    "summary": "Assign automatically a workflow at sale creation",
    "version": "18.0.1.1.0",
    "category": "Sales Management",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale_automatic_workflow",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        "views/sale_workflow_process_view.xml",
    ],
    "installable": True,
}
