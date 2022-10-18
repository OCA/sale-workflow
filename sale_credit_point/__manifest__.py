# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Credit Points",
    "version": "11.0.1.0.3",
    "category": "Sales",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": [
        "sale",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "data/res_currency.xml",
        "views/partner.xml",
        "views/point_history.xml",
        "wizards/manage_credit_point.xml",
    ],
}
