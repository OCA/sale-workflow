# Copyright 2025 Escodoo (http://escodoo.com.br/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Sales Invoice Plan Report",
    "summary": "Add invoice plan to sales order/quotation PDF report",
    "version": "18.0.1.0.0",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": [
        "sale_invoice_plan",
    ],
    "data": [
        "views/report_saleorder.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["kaynnan", "marcelsavegnago"],
    "installable": True,
    "auto_install": False,
}
