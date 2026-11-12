# Copyright 2026 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sales Invoice Plan Allocation",
    "summary": "Allocate each sales invoice plan to specific sales order lines",
    "version": "18.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": ["sale_invoice_plan"],
    "data": [
        "security/sale_invoice_plan_allocation_security.xml",
        "security/ir.model.access.csv",
        "views/sale_invoice_plan_views.xml",
        "views/sale_order_views.xml",
        "wizards/sale_create_invoice_plan_view.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Alpha",
    "maintainers": ["Saran440"],
    "installable": True,
}
