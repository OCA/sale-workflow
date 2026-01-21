# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Automatic Workflow Force Invoiced",
    "summary": "Force Invoice as an automatic workflow option",
    "version": "18.0.1.0.0",
    "author": "Sygel, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": ["sale_force_invoiced", "sale_automatic_workflow"],
    "data": [
        "data/automatic_workflow_data.xml",
        "views/sale_workflow_process_view.xml",
    ],
    "installable": True,
}
