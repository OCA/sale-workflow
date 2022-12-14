# Copyright 2019 Akretion (<http://www.akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Sub State",
    "version": "12.0.1.0.0",
    "category": "Tools",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-workflow",
    "license": "AGPL-3",
    "depends": ["base_substate", "sale_management"],
    "data": ["views/sale_views.xml",
             'data/sale_substate_mail_template_data.xml',
             'data/sale_substate_data.xml',
             ],
    "demo": [
        'data/sale_substate_demo.xml',
    ],
    "installable": True,
}
