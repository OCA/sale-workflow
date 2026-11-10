# Copyright 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Creation Date",
    "summary": """Show the field 'create date' on the Sale Orders list view,
        all sale order form views (no matter of the state) and on the search view.
        By default, Odoo does not display this field,
        and it may be important for some users
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "category": "Sales",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["sale"],
    "data": ["views/sale_order.xml"],
    "installable": True,
}
