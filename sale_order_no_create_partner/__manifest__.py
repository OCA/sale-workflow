# Copyright 2020 PESOL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': "Sale Order no create partner",
    'summary': "Avoid creating a new partner in the sales order section",
    'version': '12.0.1.0.0',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'author': 'PESOL, Odoo Community Association (OCA)',
    "maintainers": [
        'MarioVillaescusaPesol'
    ],
    'license': 'AGPL-3',
    'depends': [
        'sale'
    ],
    'data': [
        'views/sale_order_no_create_partner_view.xml',
    ]
}
