# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

{
    "name": "Sale Stock Expiry Date on Qty at Date widget",
    "summary": "Show next Expiry Date on Qty at Date Widget",
    "version": "16.0.1.0.1",
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
        "product_expiry",
    ],
    "data": [
        "views/sale_order_line_view.xml",
        "views/stock_quant_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_stock_expiry_date_on_qty_at_date_widget/static/src/**/*",
        ],
    },
}
