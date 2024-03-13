{
    "name": "Sale By Packaging",
    "summary": "Manage sale of packaging",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Ametras - Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sell_only_by_packaging"],
    "data": [
        "views/product_packaging.xml",
        "views/sale_order_line.xml",
    ],
}
