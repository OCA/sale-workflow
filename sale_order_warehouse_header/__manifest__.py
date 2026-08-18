# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Sale Order Warehouse Header",
    "summary": """
        Moves warehouse field in sales orders form to header,
        so it becomes more accessible.
            Improvements in the search view:
            - Filter by warehouse.
            - Group by warehouse.
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "19.0.1.0.0",
    "category": "Inventory/Purchase",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale_stock",
    ],
    "data": [
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
