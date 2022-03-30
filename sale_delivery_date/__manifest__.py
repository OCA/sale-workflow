# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Sale Delivery Date",
    "summary": (
        "Postpones delivery dates based on customer preferences, "
        "and/or warehouse configuration."
    ),
    "version": "14.0.1.1.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "maintainers": ["mmequignon"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        # core
        "delivery",
        "resource",
        "sale_stock",
        # OCA/partner-contact
        "partner_tz",
        # OCA/stock-logistics-workflow
        "stock_partner_delivery_window",
        # OCA/stock-logistics-warehouse
        "stock_warehouse_calendar",
        # OCA/sale-workflow
        "sale_order_line_date",
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
    "development_status": "Alpha",
}
