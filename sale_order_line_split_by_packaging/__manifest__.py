# Copyright 2026 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Line Split by Packaging",
    "summary": "Sale Order Line Split by Packaging",
    "version": "18.0.1.0.0",
    "category": "sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": " Akretion, Odoo Community Association (OCA)",
    "maintainers": ["mathieudelva"],
    "license": "AGPL-3",
    "depends": [
        "sale_pricelist_packaging",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "wizard/split_order_line_wizard.xml",
    ],
}
