# Copyright 2021 Daniel Dominguez, Manuel Calero - https://xtendoo.es
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sale Order Delivery Product",
    "summary": """Insert a button on the sales order to directly access
                the first of the deliveries and make the delivery.""",
    "version": "13.0.1.0.0",
    "category": "Sale",
    "website": "https://xtendoo.es",
    "author": "Daniel Domínguez, Manuel Calero, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["sale_management", "sale", "stock"],
    "data": ["views/sale_order_views.xml"],
}
