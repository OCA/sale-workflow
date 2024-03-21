# Copyright 2024 Akretion (http://www.akretion.com/)
# @author: Olivier Nibart <olivier.nibart@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "sale_automatic_workflow_stock_location_route",
    "summary": """
        Allows to set a specific route on sale order lines at confirmation time.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_stock",
        "sale_automatic_workflow",
    ],
    "data": [
        "views/sale_workflow_process_view.xml",
    ],
}
