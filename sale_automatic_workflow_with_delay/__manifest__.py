# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Sale Automatic Workflow With Delay",
    "summary": "Allow to add a delay when processing workflow options.",
    "version": "14.0.1.0.0",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_automatic_workflow"],
    "data": ["views/sale_workflow_process_view.xml", "data/ir_cron.xml"],
}
