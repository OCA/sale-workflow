# Copyright 2021 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale production State",
    "summary": "Show the production state on the sale order",
    "version": "14.0.1.0.0",
    "category": "Product",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["mrp_sale_info"],
    "data": [
        "views/sale_order.xml",
    ],
    "demo": [],
}
