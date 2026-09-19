# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Stock Qty By Warehouse",
    "summary": """Display the quantity by warehouse for a product inside a
    sale order line""",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_stock"],
    "data": ["views/sale_order.xml"],
    "maintainers": ["benwillig"],
    "assets": {
        "web.assets_backend": [
            "sale_stock_qty_by_warehouse/static/src/widgets/qty_by_warehouse_widget.esm.js",
            "sale_stock_qty_by_warehouse/static/src/widgets/qty_by_warehouse_widget.xml",
        ],
    },
}
