# Copyright 2021 Xtendoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Line Hide Create Product",
    "summary": """
        This module change the views of the sales lines so that it does not allow
        the creation of products on the fly
    """,
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Xtendoo,Odoo Community Association (OCA)",
    "maintainers": ["manuelcalerosolis"],
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale_stock"],
    "data": ["views/sale_order_view.xml"],
}
