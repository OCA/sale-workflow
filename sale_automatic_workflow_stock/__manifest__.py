# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Automatic Workflow Stock",
    "version": "18.0.1.0.1",
    "category": "Sales Management",
    "license": "AGPL-3",
    "author": "Akretion, "
    "Camptocamp, "
    "Sodexis, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_automatic_workflow", "sale_stock"],
    "data": [
        "views/sale_order_views.xml",
        "views/sale_workflow_process_views.xml",
        "data/automatic_workflow_data.xml",
    ],
    "auto_install": True,
    "pre_init_hook": "pre_init_hook",
}
