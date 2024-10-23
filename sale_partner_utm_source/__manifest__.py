# Copyright 2024 Trobz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Partner Source",
    "summary": "This module adds the use of utm source in sales",
    "version": "17.0.1.0.0",
    "category": "Sales Management",
    "author": "Trobz, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["account", "sale", "partner_utm_source"],
    "website": "https://github.com/OCA/sale-workflow",
    "data": [
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
    ],
}
