# Copyright 2026 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Sale Invoice To Partner",
    "version": "19.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "category": "Sales/Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": "Set on a customer a separate partner in charge of receiving "
    "and paying its invoices, used as the invoice address on sales orders.",
    "depends": [
        "sale",
    ],
    "data": [
        "views/res_partner_views.xml",
    ],
}
