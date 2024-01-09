# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project From Quotation",
    "version": "16.0.1.0.0",
    "summary": """Create project and tasks from quotation without confirming it""",
    "author": "Cetmix, Odoo Community Association (OCA)",
    "category": "Sales/CRM",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_project"],
    "live_test_url": "https://demo.cetmix.com",
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "wizards/project_from_quotation_views.xml",
        "views/sale_order_views.xml",
        "views/project_task_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
