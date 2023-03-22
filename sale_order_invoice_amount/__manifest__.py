# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    "name": "Sale Order Invoice Amount",
    "version": "16.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "license": "LGPL-3",
    "summary": "Display the invoiced and uninvoiced total in the sale order",
    "depends": [
        "sale",
        "account",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "assets": {
        "web.assets_backend": [
            "sale_order_invoice_amount/static/src/xml/*",
        ],
    },
}
