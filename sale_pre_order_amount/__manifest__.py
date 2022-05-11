{
    "name": "Sale Pre Order Amount",
    "version": "15.0.1.0.0",
    "category": "Inventory",
    "author": "ERP Harbor Consulting Services, Nitrokey GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": """
    This module adds a smart button in Product to open
    the confirmed/assigned Stock Moves (Sale Pre-Order Amount)
    of the related product.
     """,
    "depends": [
        "sale_management",
        "sale_stock",
    ],
    "data": [
        "views/nitrokey_pre_order_view.xml",
        "views/product_view.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
