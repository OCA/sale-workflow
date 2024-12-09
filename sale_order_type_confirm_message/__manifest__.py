# Copyright 2020 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Order Type Confirm Message",
    "summary": "Confirmation requirement when validating sale",
    "version": "17.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/OCA/sale-workflow",
    "author": "Sygel, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_order_type"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/sale_order_type_confirm_message_wizard_view.xml",
        "views/sale_order_type_view.xml",
    ],
}
