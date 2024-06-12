# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Readonly Security",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "version": "15.0.1.0.0",
    "depends": ["sale"],
    "license": "AGPL-3",
    "category": "Sales Management",
    "data": [
        "security/sale_readonly_security_security.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "maintainers": ["victoralmau"],
}
