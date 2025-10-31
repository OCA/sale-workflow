# Copyright 2025 ForgeFlow (http://www.forgeflow.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Create Invoices Hook",
    "summary": "Add hooks on _create_invoices method",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale"],
    "application": False,
    "installable": True,
    "post_load": "post_load_hook",
}
