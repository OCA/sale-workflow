# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

{
    "name": "Sale Order Invoice Amount",
    "version": "17.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "license": "LGPL-3",
    "summary": "Improves Sales Order invoiced/to invoice amount calculation "
    "based on product quantities when the company setting is enabled.",
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_order_view.xml",
        "views/sale_order_config_settings.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "sale_order_invoice_amount/static/src/xml/tax_totals.xml",
        ],
    },
}
