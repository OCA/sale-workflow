# -*- coding: utf-8 -*-
{
    'name': 'Sale product bundle layout',
    'category': 'Sale',
    'author': 'Anybox, Odoo Community Association (OCA)',
    'version': '1.0',
    'sequence': 150,
    'website': 'http://anybox.fr',
    'summary': "Sale product bundle layout",
    'depends': [
        'sale_product_bundle',
        'sale_layout',
    ],
    'data': [
        'views/product_bundle.xml',
    ],
    'demo': [
        'demo/product_bundle.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
