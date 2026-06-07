# Copyright 2026 OpenStudio SAS
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    "name": "Sale Partner Sale Contact",
    "summary": "Add sale contact person field to quotations, orders, and invoices",
    "version": "19.0.1.0.0",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "OpenStudio SAS, Odoo Community Association (OCA)",
    "maintainers": ["maisim"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_management",
        "account",
    ],
    "data": [
        "security/ir_rules.xml",
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
        "reports/sale_order_report_templates.xml",
        "reports/account_invoice_report_templates.xml",
    ],
}
