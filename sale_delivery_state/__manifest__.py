# Copyright 2018 Akretion (http://www.akretion.com).
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale delivery State",
    "summary": "Show the delivery state on the sale order",
    "version": "16.0.1.0.0",
    "category": "Product",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale"],
    "data": [
        "views/sale_order_views.xml",
    ],
    "demo": [
        "demo/sale_demo.xml",
    ],
}
