# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Custom Rounding",
    "summary": "Custom taxes rounding method in sale orders",
    "version": "15.0.1.0.1",
    "category": "Sales",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account_invoice_custom_rounding", "sale"],
    "data": [
        "views/sale_views.xml",
    ],
}
