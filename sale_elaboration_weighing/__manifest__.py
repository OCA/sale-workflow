# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Weighing assistant elaborations",
    "summary": "Weighing assistant extension for elaborations",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "category": "Inventory",
    "depends": [
        "stock_weighing",
        "sale_elaboration",
    ],
    "data": ["views/stock_move_views.xml"],
    "assets": {
        "web.assets_backend": [
            "sale_elaboration_weighing/static/src/scss/stock_weighing.scss",
        ],
    },
    "installable": True,
}
