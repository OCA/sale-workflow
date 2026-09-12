# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Priority Partner",
    "summary": "Define a default sale order priority on the customer",
    "version": "19.0.1.0.0",
    "category": "Sale Workflow",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_order_priority"],
    "data": ["views/res_partner.xml"],
}
