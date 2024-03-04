# Copyright 2024 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sales Invoice Plan - Create Invoice in Batch",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale_invoice_plan"],
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales Management",
    "data": [
        "data/sequence.xml",
        "security/sale_invoice_plan_batch_security.xml",
        "security/ir.model.access.csv",
        "views/sale_invoice_plan_batch.xml",
    ],
}
