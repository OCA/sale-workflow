# Copyright 2023 Nextev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order General Discount Payment Term",
    "summary": "General discount per sale order set on payment term",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Nextev," "Ooops," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["odooNextev"],
    "application": False,
    "installable": True,
    "depends": ["sale_order_general_discount"],
    "data": ["views/account_payment_term_view.xml"],
}
