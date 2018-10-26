# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Order Secondary Unit',
    'summary': 'Sale product in a secondary unit',
    'version': '11.0.1.0.1',
    'development_status': 'Beta',
    'category': 'Sale',
    'website': 'https://github.com/OCA/sale-workflow',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': True,
    'depends': [
        'sale',
        'product_secondary_unit',
    ],
    'data': [
        'views/product_views.xml',
        'views/sale_order_views.xml',
    ],
}
