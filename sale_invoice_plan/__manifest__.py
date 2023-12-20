# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Sales Invoice Plan",
    "summary": "Add to sales order, ability to manage future invoice plan",
    "version": "13.0.1.0.2",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow/",
    "category": "Sales",
    "depends": ["account", "sale_management", "sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/sale_create_invoice_plan_view.xml",
        "wizard/sale_make_planned_invoice_view.xml",
        "views/sale_view.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["kittiu"],
}
