# Copyright 2021 Manuel Calero Solís (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Order Delivered Weight',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'Xtendoo, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'summary': 'Sale Order Delivered Weight',
    'depends': [
        'sale',
        'sale_order_weight',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
}
