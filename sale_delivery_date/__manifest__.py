# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Sale Delivery Date",
    "summary": (
        "Postpones delivery dates based on customer preferences, "
        "and/or warehouse configuration."
    ),
    "version": "14.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "maintainers": ["mmequignon"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        "delivery",
        "partner_tz",
        "sale_stock",
        "stock_partner_delivery_window",
        "stock_warehouse_calendar",
    ],
    "data": [
        # reports
        "reports/sale_order.xml",
        "reports/stock_picking.xml",
        # views
        "views/res_partner.xml",
        "views/stock_picking.xml",
        "views/stock_warehouse.xml",
    ],
    "external_dependencies": {
        "python": ["openupgradelib"],
    },
    "pre_init_hook": "pre_init_hook",
}
