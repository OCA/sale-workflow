# Copyright 2020 Akretion Renato Lima <renato.lima@akretion.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale MRP BOM",
    "category": "Sale",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "version": "15.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "summary": "Allows define a BOM in the sales lines.",
    "depends": [
        "sale_stock",
        "mrp",
    ],
    "data": [
        "security/security.xml",
        "views/sale_order.xml",
        "views/sale_order_line.xml",
    ],
    "installable": True,
}
