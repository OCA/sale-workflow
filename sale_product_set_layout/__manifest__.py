# -*- coding: utf-8 -*-
{
    'name': 'Sale product set layout',
    'category': 'Sale',
    'author': 'Anybox, Odoo Community Association (OCA)',
    'version': '10.0.1.0.0',
    'sequence': 150,
    'website': 'http://anybox.fr',
    'summary': "Sale product set layout",
    'depends': [
        'sale_product_set',
    ],
    'data': [
        'views/product_set.xml',
        'security/groups.xml',
    ],
    'demo': [
        'demo/product_set.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
