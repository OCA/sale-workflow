# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
{
    "name": "Sale order line hidden in report",
    "summary": "Hide order lines in reports",
    "version": "16.0.1.0.1",
    "development_status": "Alpha",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["chienandalu", "rafaelbn"],
    "license": "LGPL-3",
    "depends": ["sale"],
    "data": [
        "views/report_invoice_document.xml",
        "views/report_saleorder_document.xml",
        "views/account_move_views.xml",
        "views/sale_order_views.xml",
    ],
}
