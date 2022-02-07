# Copyright (C) 2022 Akretion
# License ALGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Line Partner",
    "version": "14.0.1.0.0",
    "category": "Tools",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "summary": "Allow to list partner sale lines and add ones",
    "depends": [
        "sale_order_line_input",
        "sale_commercial_partner",
    ],
    "data": [
        "views/sale.xml",
        "views/partner.xml",
    ],
    "demo": [],
    "maintainers": ["bealdav"],
}
