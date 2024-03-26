# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "sale_stock_prebook_stock_available_to_promise_release",
    "summary": "Extends the previous available qty to promised with moves of a reservation",
    "version": "14.0.1.0.0",
    "author": "MT Software, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_stock_prebook",
        "stock_available_to_promise_release",
    ],
    "maintainers": ["mt-software-de"],
    "license": "LGPL-3",
    "auto_install": True,
}
