# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Downpayment Product",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Sale",
    "depends": [
        # Odoo Core
        "sale",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        "views/product_template.xml",
        "wizard/sale_advance_payment_inv.xml",
    ],
    "installable": True,
}
