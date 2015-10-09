# -*- coding: utf-8 -*-

{
    'name': 'Sale product set',
    'category': 'Sale',
    'author': 'Anybox, Odoo Community Association (OCA)',
    'version': '8.0.1.0.0',
    'sequence': 150,
    'website': 'http://anybox.fr',
    'summary': "Sale product set",
    'depends': [
        'sale',
    ],
    'data': [
        'views/product_set.xml',
        'wizard/product_set_add.xml',
        'views/sale_order.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/product_set.xml',
        'demo/product_set_line.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
