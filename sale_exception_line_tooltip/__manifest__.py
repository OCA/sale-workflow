# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Exception Line Tooltip",
    "summary": "Shows tooltips on sale order lines that have exceptions",
    "version": "19.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": [
        # OCA/sale-workflow
        "sale_exception",
    ],
    "data": [
        # Views
        "views/sale_order_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_exception_line_tooltip/static/src/fields/sale_exception_line_tooltip_field/*",
        ],
    },
    "installable": True,
}
