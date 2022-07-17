# Copyright (c) 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Pricelist Tax",
    "version": "14.0.1.0.0",
    "category": "Sale",
    "author": "Akretion, Odoo Community Association (OCA)",
    "depends": [
        "sale",
    ],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        "views/pricelist_view.xml",
        "views/account_tax_view.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "license": "AGPL-3",
}
