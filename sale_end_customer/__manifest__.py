# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale End Customer",
    "summary": "Track End Customer on sales orders and customer invoices",
    "version": "16.0.1.0.0",
    "category": "Sale",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "license": "AGPL-3",
    "data": [
        "reports/account_invoice_report_views.xml",
        "reports/sale_report_views.xml",
        "views/account_move_views.xml",
        "views/sale_order_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
