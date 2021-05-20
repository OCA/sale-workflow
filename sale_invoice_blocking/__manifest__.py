# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Invoice Blocking",
    "summary": "Allow you to block the creation of invoices from a sale order.",
    "version": "14.0.1.0.0",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "depends": ["sale", "sales_team"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_invoice_blocking_reason_view.xml",
        "views/sale_order.xml",
        "views/menus.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
}
