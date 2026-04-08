# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    "name": "sale_order_line_section",
    "summary": "Section on sale order line",
    "version": "19.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale",
    ],
    "data": [
        "views/sale_order_view.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
