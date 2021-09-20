# Copyright (C) 2021 Manuel Calero <manuelcalero@xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Automatic Workflow Send Invoice",
    "version": "13.0.1.2.2",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "Xtendoo, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_automatic_workflow"],
    "data": [
        "views/sale_workflow_process_view.xml",
        "data/automatic_workflow_data.xml",
    ],
}
