# Copyright 2026 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Approval Block",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": "Block sale orders with approval reasons",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "sale_exception",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/sale_order_approval_block_security.xml",
        "data/sale_exception_data.xml",
        "views/sale_approval_block_reason_view.xml",
        "views/sale_order_view.xml",
    ],
}
