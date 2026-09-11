# Copyright 2026 Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Sale Stock Delivery Address Text",
    "version": "19.0.1.0.0",
    "category": "Sales/Sales",
    "summary": "Free-text delivery address on sale orders, shown on the "
    "related transfers and printed on delivery reports",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "LGPL-3",
    "depends": ["sale_stock"],
    "data": [
        "views/sale_order_views.xml",
        "views/stock_picking_views.xml",
        "reports/stock_picking_reports.xml",
    ],
    "installable": True,
}
