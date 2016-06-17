# -*- coding: utf-8 -*-
{
    'name': 'Sale product layout',
    'category': 'Sale',
    'author': 'Mirounga, Odoo Community Association (OCA)',
    'version': '8.0.1.0.0',
    'sequence': 150,
    'website': 'http://www.mirounga.fr',
    'summary': """Add default layout on product,
    to add it automatically on the sale order line""",
    'depends': [
        'sale_layout',
    ],
    'data': [
        'views/product.xml',
    ],
    'demo': [
        'demo/product.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
