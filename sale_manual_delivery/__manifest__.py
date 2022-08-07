# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Manual Delivery",
    "category": "Sale",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "12.0.2.0.1",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": "Create manually your deliveries",
    "depends": [
        "delivery",
        "sale_stock",
        "sales_team",
    ],
    "data": [
        "views/crm_team_view.xml",
        "views/sale_order_view.xml",
        "wizard/manual_proc_view.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
