# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

{
    "name": "Sale Stock Reservation Issue on Qty at Date widget",
    "summary": "Warn user when a reservation issue will happen when confirming an order",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_stock_reservation_issue_on_qty_at_date_widget/static/src/**/*",
        ],
    },
}
