# Copyright 2022 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Automatic Workflow Advance",
    "version": "15.0.1.0.0",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_automatic_workflow", "sale_advance_payment"],
    "data": [
        "data/automatic_workflow_data.xml",
        "views/sale_workflow_process_view.xml",
    ],
    "installable": True,
}
