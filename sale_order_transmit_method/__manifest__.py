# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Transmit Method",
    "summary": """
        Set transmit method (email, post, portal, ...) in sale order and
        propagate it to invoices""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["account_invoice_transmit_method", "sale"],
    "data": ["views/sale_order.xml"],
}
