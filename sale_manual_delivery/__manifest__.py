# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Manual Delivery",
    "category": "Sale",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": "Create your deliveries manually",
    "depends": [
        "stock_delivery",
        "sale_stock",
        "sales_team",
        "sale_stock_reference_by_line",
    ],
    "data": [
        "security/manual_delivery.xml",
        "views/crm_team.xml",
        "views/sale_order.xml",
        "wizard/manual_delivery.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
