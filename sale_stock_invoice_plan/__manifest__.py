# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Sales Stock Invoice Plan",
    "summary": "Add to sales order, ability to manage future invoice plan",
    "version": "15.0.1.0.0",
    "author": "Ecosoft,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": ["sale_invoice_plan", "sale_stock"],
    "data": ["security/ir.model.access.csv"],
    "installable": True,
    "development_status": "Alpha",
    "maintainers": ["kittiu"],
    "auto_install": True,
}
