# -*- coding: utf-8 -*-

{
    'name': 'Sale product set',
    'category': 'Sale',
    'author': 'Anybox, Odoo Community Association (OCA)',
    'version': '1.0',
    'sequence': 150,
    'website': 'http://anybox.fr',
    'summary': "Sale product set",
    'depends': [
        'sale',
    ],
    'data': [
        'views/product_set.xml',
        'wizard/sale_order_set.xml',
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
