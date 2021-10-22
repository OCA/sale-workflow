# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Stock Last Date",
    "summary": "Displays last delivery date in sale order lines",
    "version": "13.0.1.0.0",
    "development_status": "Beta",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_stock"],
    "data": ["views/sale_order_view.xml", "reports/sale_report_view.xml"],
    "pre_init_hook": "pre_init_hook",
}
