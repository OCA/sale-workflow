# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale Warehouse Calendar",
    "summary": (
        "Computes the sales order `expected_date` and delivery order "
        "`scheduled_date` with respect to the warehouse calendar"
    ),
    "version": "13.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "maintainers": ["mmequignon"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale_cutoff_time_delivery", "stock_warehouse_calendar"],
    "data": ["views/stock_warehouse.xml"],
}
