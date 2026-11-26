# Copyright 2026 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Order Invoicing Avoid Zero Amount",
    "summary": "Zero-amount sale order lines have nothing to invoice",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Sales Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale"],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
