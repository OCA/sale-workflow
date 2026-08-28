# Copyright 2026 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Procurement Group by Line MRP",
    "summary": "Fixes double procurement on nested kit products when "
    "sale_procurement_group_by_line and sale_mrp are both installed.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Sales",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_procurement_group_by_line",
        "sale_mrp",
    ],
    "data": [],
    "auto_install": True,
}
