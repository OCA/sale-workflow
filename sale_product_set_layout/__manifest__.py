# -*- coding: utf-8 -*-
{
    'name': 'Sale product set layout',
    'category': 'Sale',
    'author': 'Anybox, Odoo Community Association (OCA)',
    'version': '8.0.1.0.0',
    'sequence': 150,
    'website': 'http://anybox.fr',
    'summary': "Sale product set layout",
    'depends': [
        'sale_product_set',
        'sale_layout',
    ],
    'data': [
        'views/product_set.xml',
    ],
    'demo': [
        'demo/product_set.xml',
    ],
    'installable': False,
    'application': False,
    'auto_install': False,
}
