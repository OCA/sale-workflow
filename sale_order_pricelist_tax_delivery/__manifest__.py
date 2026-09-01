# Copyright 2025 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Pricelist Tax Delivery",
    "summary": "Glue module between delivery and sale_order_pricelist_tax",
    "version": "14.0.1.0.0",
    "category": "sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "sale_order_pricelist_tax",
        "delivery",
    ],
    "data": [],
}
