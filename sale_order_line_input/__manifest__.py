# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Sale Order Line Input',
    'summary': 'Search, create or modify directly sale order lines',
    'version': '11.0.1.0.0',
    'development_status': 'Beta',
    'category': 'Sales',
    'website': 'https://github.com/OCA/sale-workflow',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale_order_line_view.xml',
    ],
}
