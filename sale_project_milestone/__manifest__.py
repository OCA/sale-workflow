# Copyright 2025 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Project Milestone",
    "summary": """
        Create milestones in new or existing projects from sale order lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Innovyou, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_project",
        "project",
        "hr_timesheet",
    ],
    "data": [
        "views/product_template_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "development_status": "Beta",
}
