# -*- coding: utf-8 -*-

{
    'name': 'Sale Manual Delivery',
    'category': 'Sale',
    'author': 'Camptocamp SA, Odoo Community Association (OCA)',
    'version': '10.0.1.0.0',
    'sequence': 150,
    'website': 'http://camptocamp.com',
    'summary': "Sale product set",
    'depends': [
        'delivery',
        'sale',
        'sales_team',
    ],
    'data': [
        'views/crm_team_view.xml',
        'views/sale_order_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
