{
    "name": "Sale Order Lot Selection",
    "version": "18.0.1.2.4",
    "category": "Sales Management",
    "author": "Odoo Community Association (OCA), Agile Business Group",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["sale_stock", "stock_restrict_lot"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "reports/sale_report_views.xml",
    ],
    "demo": ["demo/sale_demo.xml"],
    "maintainers": ["bodedra"],
    "installable": True,
}
