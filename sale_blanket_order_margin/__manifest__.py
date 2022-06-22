# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Blanket Orders Margin",
    "category": "Sale",
    "license": "AGPL-3",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "version": "15.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": "Blanket Orders",
    "depends": ["sale_blanket_order", "sale_margin"],
    "data": [
        "views/sale_blanket_order_views.xml",
    ],
    "installable": True,
}
