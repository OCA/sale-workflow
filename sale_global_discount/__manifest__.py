# Copyright 2020 Tecnativa - David Vidal
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Global Discount",
    "version": "16.0.1.0.1",
    "category": "Sales Management",
    "author": "Tecnativa," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["account_global_discount", "sale"],
    "data": ["views/sale_order_views.xml", "views/report_sale_order.xml"],
    "application": False,
    "installable": True,
}
