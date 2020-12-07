# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale payment sheet",
    "summary": "Allow to create invoice payments to commercial users without "
    "accounting permissions",
    "version": "13.0.1.0.0",
    "development_status": "Beta",
    "category": "Account",
    "website": "https://github.com/OCA/sale-workflow/",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["sergio-teruel"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "report/report_sale_payment_sheet_summary.xml",
        "report/sale_payment_sheet_report.xml",
        "views/res_users_views.xml",
        "views/sale_payment_sheet_views.xml",
        "views/sale_payment_sheet_menu.xml",
        "wizards/sale_invoice_payment_view.xml",
    ],
}
