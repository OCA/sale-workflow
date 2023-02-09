# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sale Exception",
    "summary": "Custom exceptions on sale order",
    "version": "16.0.1.0.0",
    "category": "Generic Modules/Sale",
    "author": "Akretion, "
    "Sodexis, "
    "Camptocamp, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale", "base_exception"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/sale_exception_data.xml",
        "wizard/sale_exception_confirm_view.xml",
        "views/sale_view.xml",
    ],
    "demo": ["demo/sale_exception_demo.xml"],
}
