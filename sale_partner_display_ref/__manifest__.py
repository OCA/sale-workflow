# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Partner Display Reference",
    "summary": "Wire the partner reference prefix into Sales views.",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["partner_display_ref", "sale"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
