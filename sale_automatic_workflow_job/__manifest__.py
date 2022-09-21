# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Automatic Workflow Job",
    "summary": "Execute sale automatic workflows in queue jobs",
    "version": "14.0.1.0.1",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_automatic_workflow", "queue_job"],
    "data": [
        "data/queue_job_data.xml",
    ],
}
